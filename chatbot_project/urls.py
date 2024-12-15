from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('main_page.urls')),  # main_page 앱의 URL 포함
    path('', include('main_page.urls')),        # 기본 URL을 main_page로 설정
    path('character/', include('character_info.urls')),
    path('chatbot/', include('chatbot.urls')),
]