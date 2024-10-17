from django.db import models

class ChatMessage(models.Model):
    user_message = models.TextField()    # 사용자 입력
    bot_response = models.TextField()    # 챗봇의 응답
    created_at = models.DateTimeField(auto_now_add=True)  # 메시지 생성 시간