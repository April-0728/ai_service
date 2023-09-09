from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.log_service.views.log_reduce_view import LogReduceView

router = SimpleRouter()
router.register(r"log_reduce", LogReduceView, basename="log_reduce")

urlpatterns = [
    path('api/logs_algorithm/', include(router.urls)),
]
