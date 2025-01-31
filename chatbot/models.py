from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True)  # 세션 제목 (선택사항)
    is_active = models.BooleanField(default=True)  # 활성 세션 표시
    last_message_time = models.DateTimeField(auto_now=True)  # 마지막 메시지 시간

    class Meta:
        ordering = ['-last_message_time']  # 최신 메시지 순으로 정렬

    def __str__(self):
        return f"Session {self.id} - {self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_messages_count(self):
        return self.messages.count()

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.CharField(
        max_length=10, 
        choices=SENDER_CHOICES, 
        default='user'
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # 메시지 읽음 상태

    class Meta:
        ordering = ['timestamp']  # 시간순 정렬

    def __str__(self):
        return f"{self.session.user.username} - {self.sender}: {self.text[:50]}"

    def save(self, *args, **kwargs):
        # 메시지 저장 시 세션의 last_message_time 업데이트
        super().save(*args, **kwargs)
        self.session.last_message_time = self.timestamp
        self.session.save()

