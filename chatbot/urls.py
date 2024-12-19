from django.urls import path
from django.views.generic import RedirectView
from django.views.decorators.csrf import ensure_csrf_cookie
from . import views

urlpatterns = [
    path('', ensure_csrf_cookie(views.chatbot_view), name='chatbot'),
    path('chatbot/', ensure_csrf_cookie(views.chatbot_view), name='chatbot'),
    path('chatbot/search_character/', views.search_character, name='search_character'),
]
