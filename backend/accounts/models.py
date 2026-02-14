from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    DIALECT_CHOICES = [("najdi","najdi"),("hijazi","hijazi"),("khaliji","khaliji")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_dialect = models.CharField(max_length=16, choices=DIALECT_CHOICES, default="najdi")
    default_voice_actor = models.CharField(max_length=64, default="male_01")
    created_at = models.DateTimeField(auto_now_add=True)
