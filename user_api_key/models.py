from django.db import models
from django.contrib.auth.models import User

class CharacterInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ocid = models.CharField(max_length=255, unique=True)
    character_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.character_name} (OCID: {self.ocid})"
