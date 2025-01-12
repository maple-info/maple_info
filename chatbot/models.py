from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 세션 소유 사용자
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간 자동 설정

    def __str__(self):
        return f"Session of {self.user.username} at {self.created_at}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, default='user')  # 선택 가능 값 추가
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.user.username} - {self.sender}: {self.text[:20]}"


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(
        ChatMessage, on_delete=models.CASCADE, related_name='history'
    )  # ChatMessage와 연결
    timestamp = models.DateTimeField(auto_now_add=True)  # 중복 방지

    def __str__(self):
        return f"History of {self.user.username} - {self.message.sender}: {self.message.text[:20]}"
