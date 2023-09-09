from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class LogReduceView(ViewSet):
    @action(methods=["POST"], detail=False, url_path=r"predict")
    def predict(self, request):
        return Response({'status': 'ok'})
