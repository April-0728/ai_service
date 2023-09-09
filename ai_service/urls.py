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
from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from apps.log_service.router import log_service_router

apis = NinjaAPI()
apis.add_router('/logs', log_service_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', apis.urls),
]
