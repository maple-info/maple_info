# chatbot_project/urls.py
from django.contrib import admin
from django.urls import path, include
from chatbot.views import chat_with_bot

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_page.urls')),  # main_page 앱
    path('character/', include('character_info.urls')), # character_info 앱
    path('chatbot/', include('chatbot.urls')), # chatbot 앱
    path('chat_with_bot/', chat_with_bot, name='chat_with_bot'),
    path('input_user_api_key/', include('user_api_key.urls')),  # user_api_key 앱
]