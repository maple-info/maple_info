from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('search_character/', views.search_character, name='search_character'),
    path('chat_with_bot/', views.chat_with_bot, name='chat_with_bot'),
    # path('chat/sessions/', views.get_chat_sessions, name='get_chat_sessions'),
    # path('chat/sessions/<int:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    # path('chat/sessions/<int:session_id>/read/', views.mark_messages_read, name='mark_messages_read'),
    # path('chat/sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),
]