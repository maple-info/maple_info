from django.urls import path
from . import views

urlpatterns = [
    path('save_chat_message/', views.save_chat_message, name='save_chat_message'),
    path('load_chat_sessions/', views.load_chat_sessions, name='load_chat_sessions'),
    path('load_chat_messages/<int:session_id>/', views.load_chat_messages, name='load_chat_messages'),
    path('load_chat_history/', views.load_chat_history, name='load_chat_history'),
    path('', views.chatbot_view, name='chatbot'),
    path('search_character/', views.search_character, name='search_character'),
    path('chat_with_bot/', views.chat_with_bot, name='chat_with_bot'),
]
