# urls.py
from django.urls import path
from . import views
from character_info.views import character_info_view


urlpatterns = [
    path('search/', views.character_search_view, name='character_search'),
    path('character/<str:character_name>/', views.character_info_view, name='character_info'),
]