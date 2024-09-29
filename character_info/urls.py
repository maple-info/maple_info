from django.urls import path
from . import views

app_name = 'character_info'

urlpatterns = [
    path('', views.character_search_view, name='search'),
    path('character/<str:character_name>/', views.character_info_view, name='info'),
]