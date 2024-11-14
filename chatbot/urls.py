from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('chat/', views.chatbot_view, name='chatbot_post'),  # 추가
    # path('character/', views.character_info_view, name='character_info'),
    path('fetch_character_info/', views.fetch_character_info, name='fetch_character_info'),
]