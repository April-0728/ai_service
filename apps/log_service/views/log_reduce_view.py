import json
import logging
import os
import os.path
import pickle

import requests
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from joblib import Parallel, delayed, parallel_backend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from tqdm import tqdm

from apps.core.utils.date_utils import DateUtils
from apps.core.utils.mongo_driver import MongoDriver
from apps.log_service.algorithm.drain3.template_miner import TemplateMiner
from apps.log_service.algorithm.drain3.template_miner_config import TemplateMinerConfig


class LogReduceView(ViewSet):

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.models = self.load_models()

    # Try to load logreduce model
    def load_models(self):
        model_url = os.environ.get("LOD_REDUCE_MODEL_PATH")
        if model_url is None:
            pass
        else:
            if os.path.exists(model_url) and os.path.isdir(model_url):
                self.logger.info(f"Scaning directory {model_url}")
                models = {}
                for file in os.listdir(model_url):
                    file_path = os.path.join(model_url, file)
                    if not file.endswith(".gitkeep"):
                        models[file] = file_path
                self.logger.info(f"Model list {models}")
                return models
            else:
                self.logger.info(f"{model_url} is not exist or not a directory")

    # predict the templates
    def predict_template(self, algorithm, model_name, logs, results):
        if algorithm == "drain3":
            if model_name == "none":
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
                model_path = self.models.get(model_name)

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
                    # no match template
                    else:
                        cluster_id = cluster.cluster_id
                        if cluster_id not in results:
                            results[cluster_id] = {"template": cluster.get_template(), "size": 0}
                        results[cluster_id]["size"] += 1

        elif algorithm == "spell":
            pass

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "algorithm": openapi.Schema(type=openapi.TYPE_STRING, example="drain3", description="预测算法"),
                "param": openapi.Schema(type=openapi.TYPE_OBJECT, example={"partition": ":", }, description="其他参数"),
                "model_name": openapi.Schema(type=openapi.TYPE_STRING, example="model1",
                                             description="预测模板，不使用模板填none"),
                "logs": openapi.Schema(type=openapi.TYPE_ARRAY,
                                       items=openapi.Schema(type=openapi.TYPE_STRING),
                                       example=["loga", "logb"],
                                       description="日志记录")
            },
            required=["algorithm", "logs"],
        ),
        operation_description="模板预测",
        tags=["Template Prediction"],
        deprecated=False,
    )
    @action(methods=["POST"], detail=False, url_path=r"predict")
    def predict(self, request):
        data = request.data
        algorithm = data["algorithm"]
        param = data["param"]
        model_name = data["model_name"]
        logs = data["logs"]
        # results value = {template:"", size:1}

        results = {}
        self.predict_template(algorithm, model_name, logs, results)
        self.logger.info(f"-------The number of templates is {len(results)}--------")
        results_values = results.values()
        return Response({'status': 'ok',
                         'results': results_values})

    def get_datainsight_index(self, begin, end):
        begin = DateUtils.str_to_timestamp(begin)
        end = DateUtils.str_to_timestamp(end)

        driver = MongoDriver()

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
        query_results = driver.query_collection('index_ranges', query)
        index_name = [index.get('index_name') for index in query_results]
        return index_name

    @swagger_auto_schema(
        method="post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "begin": openapi.Schema(type=openapi.TYPE_STRING, example='2023-09-21 00:00:00',
                                        description="开始时间，格式：yyyy-MM-dd HH:mm:ss"),
                "end": openapi.Schema(type=openapi.TYPE_STRING, example='2023-09-21 20:00:00',
                                      description="结束时间，格式：yyyy-MM-dd HH:mm:ss"),
                "query": openapi.Schema(type=openapi.TYPE_STRING, example='ERROR', description="查询语句"),
                "algorithm": openapi.Schema(type=openapi.TYPE_STRING, example="drain3", description="预测算法"),
                "param": openapi.Schema(type=openapi.TYPE_OBJECT, example={"scroll_time": "5m"},
                                        description="其他opensearch相关参数"),
                "model_name": openapi.Schema(type=openapi.TYPE_STRING, example="model1",
                                             description="预测模板，不使用模板填none")
            },
            required=["start_time", "end_time", "sql"],
        ),
        responses={
            "200": "数据提取成功",
            "401": "Unauthorized",
            "404": "Not Found",
        },
        operation_description="提取数据进行预测",
        operation_id="data_list_emplate_prediction",
        tags=["Data List Template Prediction"],
        deprecated=False,
    )
    @action(methods=["POST"], detail=False, url_path=r"predict_from_datalist")
    def predict_from_datalist(self, request):
        results = {}
        data = request.data
        begin = data["begin"]
        end = data["end"]
        query = data["query"]
        algorithm = data["algorithm"]
        param = data["param"]
        model_name = data["model_name"]

        # get the index name from MongoDB
        index_name = self.get_datainsight_index(begin, end)

        # create the thread pool
        num_threads = 4
        try:
            # Use joblib to parallelize task execution
            with parallel_backend(backend="threading", n_jobs=num_threads):
                Parallel()(
                    delayed(self.fetch_and_predict)(index, results, query, begin, end, algorithm, param, model_name) for
                    index in index_name)

        except Exception as e:
            self.logger.error(f"Error in predict_from_datalist: {str(e)}")

        self.logger.info(f"-------The number of templates is {len(results)}--------")
        results_values = results.values()
        return Response({'status': 'ok',
                         'results': results_values})

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

            # initial query
            initial_url = f'{os.environ.get("OPENSEARCH_HOST")}/{index}/_search?scroll=1m&size=10000'
            response = requests.get(initial_url,
                                    auth=(
                                        os.environ.get("OPENSEARCH_USERNAME"),
                                        os.environ.get("OPENSEARCH_PASSWORD")),
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
                            response = requests.get(f'{os.environ.get("OPENSEARCH_HOST")}/_search/scroll',
                                                    auth=(os.environ.get("OPENSEARCH_USERNAME"),
                                                          os.environ.get("OPENSEARCH_PASSWORD")),
                                                    headers={'Content-Type': 'application/json'},
                                                    json=scroll_query, verify=False)
                            res = json.loads(response.text)
                            hits = res.get('hits', {}).get('hits', [])
                            # predict the template if hits are not none
                            if hits:
                                messages = self.fetch_messages(hits)
                                self.predict_template(algorithm, model_name, messages, results)
                            pbar.update(len(hits))
        except Exception as e:
            self.logger.error(f"Error in fetch_and_predict: {str(e)}, index_name: {index}")
