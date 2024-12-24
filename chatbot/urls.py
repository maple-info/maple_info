from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),  # 메시지 처리 엔드포인트
    path('chatbot/search_character/', views.search_character, name='search_character'),  # 캐릭터 검색 엔드포인트
]
