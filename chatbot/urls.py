from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),  # 루트 /chatbot/
    path('search_character/', views.search_character, name='search_character'),
    path('chatbot_view/', views.chatbot_view, name='chatbot_view'),
]
