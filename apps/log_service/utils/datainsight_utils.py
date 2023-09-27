from datetime import datetime

from pymongo import MongoClient


class DataInsightUtils:
    def __init__(self,mongo_url):
        self.mongo_url=mongo_url

    def format_datetime(self, time_string):
        date_object = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
        return int(date_object.timestamp())
    def get_datainsight_index(self, begin, end):
        # 对begin和end进行格式化
        begin = self.format_datetime(begin)
        end = self.format_datetime(end)
        MGclient = MongoClient(self.mongo_url)
        db = MGclient.graylog_dev
        collection = db["index_ranges"]
        # begin =
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
        index_name = []
        records = collection.find(query)
        for record in records:
            index_name.append(record["index_name"])
        return index_name
