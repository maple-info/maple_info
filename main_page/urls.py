from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_home, name='main_home'),
    path('login/google/', views.google_login, name='google_login'),
    path('accounts/google/login/callback/', views.google_callback, name='google_callback'),
    path('logout/google/', views.google_logout, name='google_logout'),  # 로그아웃 경로 추가
    path('chatbot/', views.chatbot_view, name='chatbot'),  # 챗봇 페이지 경로 추가
    path('character_info/', views.character_info_view, name='character_info'),  # 캐릭터 정보 페이지 경로 추가
]
