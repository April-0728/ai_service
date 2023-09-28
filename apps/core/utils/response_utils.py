from rest_framework import status
from rest_framework.response import Response


class ResponseUtils:
    @staticmethod
    def response_success(response_data={}):
        return Response({
            'result': response_data,
            'status': 'success',
            'reason': ''
        }, status=status.HTTP_200_OK)

    @staticmethod
    def response_failed(response_data={}, error_message=''):
        return Response({
            'result': response_data,
            'status': 'failed',
            'reason': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
