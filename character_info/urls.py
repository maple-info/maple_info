from django.urls import path
from . import views

app_name = 'character_info'

urlpatterns = [
    path('', views.character_info_view, name='search'),
    path('api/character/<str:character_name>/', views.character_info_view, name='info'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    
]