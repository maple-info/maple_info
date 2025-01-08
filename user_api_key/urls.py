from django.urls import path
from . import views


urlpatterns = [
    path('', views.input_user_api_key, name='user_api_key'),
]