from django.db import models
from django.contrib.auth.models import User

class Character(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 사용자와 1:1 관계
    google_id = models.CharField(max_length=255, unique=True)  # 구글 사용자 ID
    character_name = models.CharField(max_length=255)  # 캐릭터 이름
    character_id = models.CharField(max_length=255)  # 캐릭터 고유 ID
    server = models.CharField(max_length=255)  # 서버 정보
    last_updated = models.DateTimeField(auto_now=True)  # 마지막 업데이트 시간

    def __str__(self):
        return self.character_name
