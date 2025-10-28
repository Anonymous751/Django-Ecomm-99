from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def profile_status(self):
        return "Private" if self.is_private else "Public"

class Block(models.Model):
    blocker = models.ForeignKey(CustomUser, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(CustomUser, related_name='blocked_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)