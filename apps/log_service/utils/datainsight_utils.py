from datetime import datetime
from pymongo import MongoClient


def format_datetime(time_string):
    date_object = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return int(date_object.timestamp())


class DataInsightUtils:
    def __init__(self, mongo_url):
        self.mongo_url = mongo_url

    def get_datainsight_index(self, begin, end):
        # 对begin和end进行格式化
        begin = format_datetime(begin)
        end = format_datetime(end)

        with MongoClient(self.mongo_url) as client:
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
