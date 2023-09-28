import logging

from drf_yasg.utils import swagger_auto_schema
from joblib import Parallel, delayed, parallel_backend
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from apps.core.utils.response_utils import ResponseUtils
from apps.log_service.serializers.datainsight_log_reduce_request import DataInsightLogReduceRequest
from apps.log_service.serializers.log_reduce_request import LogReduceRequest
from apps.log_service.services.log_reduce_service import LogReduceService


class LogReduceView(ViewSet):

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.log_reduce_service = LogReduceService()

    @swagger_auto_schema(
        method="post",
        request_body=LogReduceRequest,
        operation_description="日志模式发现",
    )
    @action(methods=["POST"], detail=False, url_path=r"predict")
    def predict(self, request):
        serialize = LogReduceRequest(data=request.data)
        if serialize.is_valid():
            validated_data = serialize.validated_data
            results = {}
            self.log_reduce_service.predict_template(validated_data['algorithm'],
                                                     validated_data['model_name'],
                                                     validated_data['logs'], results)
            return ResponseUtils.response_success(results.values())
        else:
            return ResponseUtils.response_failed(error_message=serialize.errors)

    @swagger_auto_schema(
        method="post",
        request_body=DataInsightLogReduceRequest,
        operation_description="日志模式发现(DataInsight)",
    )
    @action(methods=["POST"], detail=False, url_path=r"predict_from_datainsight")
    def predict_from_datalist(self, request):
        serialize = DataInsightLogReduceRequest(data=request.data)
        if serialize.is_valid():
            validated_data = serialize.validated_data
        else:
            return ResponseUtils.response_failed(error_message=serialize.errors)
        index_name = self.log_reduce_service.get_datainsight_index(validated_data['begin'], validated_data['end'])

        num_threads = 4
        results = {}
        try:
            with parallel_backend(backend="threading", n_jobs=num_threads):
                Parallel()(
                    delayed(self.log_reduce_service.fetch_and_predict)(index, results,
                                                                       validated_data['query'], validated_data['begin'],
                                                                       validated_data['end'],
                                                                       validated_data['algorithm'],
                                                                       validated_data['param'],
                                                                       validated_data['model_name'])
                    for index in index_name)

        except Exception as e:
            self.logger.error(f"Error in predict_from_datalist: {str(e)}")

        self.logger.info(f"The number of templates is {len(results)}")
        return ResponseUtils.response_success(results.values())
