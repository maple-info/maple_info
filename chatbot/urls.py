from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('search_character/', views.search_character, name='search_character'),
    path('chat_with_bot/', views.chat_with_bot, name='chat_with_bot'),
]
