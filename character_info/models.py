# models.py
from django.db import models
import json

class CharacterInfo(models.Model):
    character_name = models.CharField(max_length=255, unique=True)
    data = models.TextField()  # JSON 형태로 모든 데이터 저장
    last_updated = models.DateTimeField(auto_now=True)

    def set_data(self, data):
        self.data = json.dumps(data)

    def get_data(self):
        return json.loads(self.data)