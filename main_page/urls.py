from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_home, name='main_home'),       # 기본 경로: /main/
    path('login/google/', views.google_login, name='google_login'),
]
