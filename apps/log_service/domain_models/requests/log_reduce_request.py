from ninja import Schema


class LogReduceRequest(Schema):
    logs: list[str]