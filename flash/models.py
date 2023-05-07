from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Flash(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    active = models.BooleanField(default=True)
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    outcome = models.BooleanField(null=True, default=None)
    votes = models.TextField(default="{}", null=False)

    def __str__(self):
        return self.title