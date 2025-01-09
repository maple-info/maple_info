from django.urls import path
from . import views

urlpatterns = [
    path('user_api_key', views.input_user_api_key, name='user_api_key'),
]
