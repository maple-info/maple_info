from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('chat/', views.chatbot_view, name='chatbot_post'),  # 추가
    path('character/', views.character_info_view, name='character_info'),
    path('send_character_info_to_chatbot/', views.send_character_info_to_chatbot, name='send_character_info_to_chatbot'),
]