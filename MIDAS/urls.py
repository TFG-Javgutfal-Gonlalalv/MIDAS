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

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", mainViews.homepage, name="homepage"),
    path("dashboard", mainViews.dashboard, name="dashboard"),
    path("stats", mainViews.get_general, name="get_general"),
    path("run/<int:run_id>/", mainViews.run_details, name="run_details"),
    path("diagrama", mainViews.diagrama, name="diagrama"),
    path("diagrama_gpt3", mainViews.diagrama_gpt3, name="diagrama_gpt3"),
    path("converter", mainViews.converter, name="converter"),
    path("register", mainViews.register_request, name="register"),
    path("login", mainViews.login_request, name="login"),
    path("logout", mainViews.logout_request, name="logout")

]
