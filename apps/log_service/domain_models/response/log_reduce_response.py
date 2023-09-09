from ninja import Schema


class LogReduceResponse(Schema):
    template: str
    logs: list[str]
    total: int
