from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chatbot_view, name='chatbot'),  # 챗봇 페이지 URL
    path('character/', views.character_info_view, name='character_info'),  # 캐릭터 정보 페이지
]