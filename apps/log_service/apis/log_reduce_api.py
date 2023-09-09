import logging
from typing import List

from ninja import Router

from apps.log_service.domain_models.requests.log_reduce_request import LogReduceRequest
from apps.log_service.domain_models.response.log_reduce_response import LogReduceResponse

log_reduce_api = Router()

logger = logging.getLogger(__name__)


@log_reduce_api.post('/predict')
def predict(request, log_reduce_request: LogReduceRequest):
    logger.info(log_reduce_request)
    results: List[LogReduceResponse] = [LogReduceResponse(template="template", logs=["log1", "log2"], total=2)]
    return results
