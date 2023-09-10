from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class LogReduceView(ViewSet):
    @action(methods=["POST"], detail=False, url_path=r"predict")
    def predict(self, request):
        """
        Input:
            {
                "algorithm": "drain3",
                "params":{

                },
                "return_raw_logs":True,
                "logs":[
                    "log a"
                    "log b"
                ]
            }
        Output:
            {
                results:[
                    {
                        "log_template":"xxx",
                        "logs":[
                        ]
                    }
                ]
            }
        """
        return Response({'status': 'ok'})
