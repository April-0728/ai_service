import json
import logging
import os
import pickle

import requests
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from pymongo import MongoClient
from tqdm import tqdm

from ai_service.components.log_reduce import MONGODB_URL, LOD_REDUCE_MODEL_PATH, OPENSEARCH_HOST, OPENSEARCH_USERNAME, \
    OPENSEARCH_PASSWORD
from apps.core.utils.date_utils import DateUtils


class LogReduceService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_reduce_model = self.load_log_reduce_models()

    def load_log_reduce_models(self):
        if LOD_REDUCE_MODEL_PATH is None:
            pass
        else:
            if os.path.exists(LOD_REDUCE_MODEL_PATH) and os.path.isdir(LOD_REDUCE_MODEL_PATH):
                self.logger.info(f"Scaning directory {LOD_REDUCE_MODEL_PATH}")

                models = {}
                for file in os.listdir(LOD_REDUCE_MODEL_PATH):
                    file_path = os.path.join(LOD_REDUCE_MODEL_PATH, file)
                    if file.endswith(".pkl"):
                        models[file] = file_path
                self.logger.info(f"Model list {models}")
                return models
            else:
                self.logger.info(f"{LOD_REDUCE_MODEL_PATH} is not exist or not a directory")

    def predict_template(self, algorithm, model_name, logs):
        results = {}
        if algorithm == "drain3":
            if model_name == "":
                config = TemplateMinerConfig()
                config.load(os.path.join(os.path.dirname(__file__), '../algorithm/drain3/drain3.ini'))
                config.profiling_enabled = False
                template_miner = TemplateMiner(config=config)

                for log in logs:
                    log = log.rstrip()
                    log = log.partition(": ")[2]
                    result = template_miner.add_log_message(log)
                    cluster_id = result["cluster_id"]
                    results[cluster_id] = {
                        "template": result["template_mined"],
                        "size": result["cluster_size"]
                    }

            else:
                # 不要每次调用都加载，要在load的时候就完成加载
                model_path = self.log_reduce_model.get(model_name)

                with open(model_path, "rb") as f:
                    predict_model = pickle.load(f)

                for log in logs:
                    log = log.rstrip()
                    log = log.partition(": ")[2]
                    cluster = predict_model.match(log)
                    # match template
                    if cluster is None:
                        if 0 not in results:
                            results[0] = {"template": "No match found", "size": 0}
                        results[0]["size"] += 1
                    else:
                        cluster_id = cluster.cluster_id
                        if cluster_id not in results:
                            results[cluster_id] = {"template": cluster.get_template(), "size": 0}
                        results[cluster_id]["size"] += 1

        elif algorithm == "spell":
            pass

        return results

    def get_datainsight_index(self, begin, end):
        begin = DateUtils.str_to_timestamp(begin)
        end = DateUtils.str_to_timestamp(end)

        with MongoClient(MONGODB_URL) as client:
            db = client.graylog_dev
            collection = db["index_ranges"]

            query = {
                "$or": [
                    {
                        "$and": [
                            {"begin": {"$gte": begin, "$lt": end}},
                            {"end": {"$gt": begin, "$lte": end}}
                        ]
                    },
                    {"begin": 0}
                ]
            }

            records = collection.find(query)
            index_name = {record["index_name"] for record in records}

        return list(index_name)

    def fetch_and_predict(self, index, results, query, begin, end, algorithm, param, model_name):
        try:
            # query condition
            initial_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "message": query
                                }
                            },
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": begin,
                                        "lte": end,
                                        "format": "yyyy-MM-dd HH:mm:ss"
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            initial_url = f'{OPENSEARCH_HOST}/{index}/_search?scroll=5m&size=10000'
            response = requests.get(initial_url,
                                    auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
                                    headers={'Content-Type': 'application/json'}, json=initial_query,
                                    verify=False)
            response.raise_for_status()

            res = json.loads(response.text)
            hits = res.get('hits', {}).get('hits', [])
            messages = [hit.get('_source', {}).get('message') for hit in hits]
            self.predict_template(algorithm, model_name, messages, results)

            total_hits = res.get('hits', {}).get('total', {}).get('value', 0)
            self.logger.info(f"The number of hits in {index} is {total_hits}")
            total_cnt = 0

            if total_hits > 0:
                with tqdm(total=total_hits, unit='doc', dynamic_ncols=True) as pbar:
                    while True:
                        scroll_id = res.get('_scroll_id')
                        cnt = len(res.get('hits', {}).get('hits', []))
                        total_cnt += cnt
                        if total_hits <= total_cnt:
                            break;
                        else:
                            scroll_query = {
                                "scroll": param["scroll_time"],
                                "scroll_id": scroll_id
                            }
                            response = requests.get(f'{OPENSEARCH_HOST}/_search/scroll',
                                                    auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
                                                    headers={'Content-Type': 'application/json'},
                                                    json=scroll_query, verify=False)
                            res = json.loads(response.text)
                            hits = res.get('hits', {}).get('hits', [])

                            if hits:
                                messages = self.fetch_messages(hits)
                                self.predict_template(algorithm, model_name, messages, results)
                            pbar.update(len(hits))
        except Exception as e:
            self.logger.error(f"Error in fetch_and_predict: {str(e)}, index_name: {index}")
