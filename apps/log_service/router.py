from ninja import Router
from apps.log_service.apis.log_reduce_api import log_reduce_api

log_service_router = Router()
log_service_router.add_router('/', log_reduce_api, tags=["LogReduce"])
