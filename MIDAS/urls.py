"""MIDAS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from main import views as mainViews
from api import views as apiViews

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="MIDAS API",
        default_version='1.0.0',
        description="API documentation of Midas",

    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", mainViews.homepage, name="homepage"),
    path("dashboard", mainViews.dashboard, name="dashboard"),
    path("stats", mainViews.get_general, name="get_general"),
    path("run/<int:run_id>/", mainViews.run_details, name="run_details"),
    path("update_run", mainViews.update_run, name="update_run"),
    path("delete_run/<int:run_id>/", mainViews.delete_run, name="delete_run"),
    path("diagrama", mainViews.diagrama, name="diagrama"),
    path("diagrama_gpt3", mainViews.diagrama_gpt3, name="diagrama_gpt3"),
    path("payment", mainViews.payment, name="payment"),
    path("converter/<int:run_id>/", mainViews.venue_text, name="converter"),
    path("register", mainViews.register_request, name="register"),
    path("login", mainViews.login_request, name="login"),
    path("logout", mainViews.logout_request, name="logout"),

    path("api/login", apiViews.login),
    path("api/runs", apiViews.getRuns, name='runs'),
    path("api/run/sql/<int:run_id>/", apiViews.getRunInSQL),
    path("api/run/<int:run_id>/", apiViews.getRun),
    path("api/run/delete/<int:run_id>/", apiViews.deleteRun),
    path("api/nlp", apiViews.nlp),
    path("api/gpt3", apiViews.ejecutar_gpt3),
    path("api/", schema_view.with_ui('swagger', cache_timeout=0), name="swagger-schema")

]