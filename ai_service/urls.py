"""
URL configuration for ai_service project.

The `urlpatterns` list routes URLs to apis. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function apis
    1. Add an import:  from my_app import apis
    2. Add a URL to urlpatterns:  path('', apis.home, name='home')
Class-based apis
    1. Add an import:  from other_app.apis import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from ai_service.components.base import DEBUG

urlpatterns = [
    # rest_framework_simplejwt自带的得到token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 刷新JWT
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 验证token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('admin/', admin.site.urls),
]

if DEBUG:
    import debug_toolbar
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view

    schema_view = get_schema_view(
        openapi.Info(
            title="API",
            default_version='v1',
            description="description",
            terms_of_service="",
            contact=openapi.Contact(email=""),
            license=openapi.License(name=""),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

for app_config in apps.get_app_configs():
    app_name = app_config.name
    try:
        # 如何app_name是apps.开头的，就import这个app的urls.py
        if app_name.startswith('apps.'):
            urls_module = __import__(f'{app_name}.urls', fromlist=['urlpatterns'])
            urlpatterns.append(path('', include(urls_module)))

    except ImportError:
        pass
