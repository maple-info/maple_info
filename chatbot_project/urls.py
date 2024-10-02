from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('character_search.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('character/', include('character_info.urls')),
    
]