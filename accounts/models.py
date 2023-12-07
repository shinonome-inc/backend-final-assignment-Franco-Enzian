from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    following = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name="followed", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['following', 'followed'], name='only_one_object')
        ]

    def clean(self):
        if self.following == self.followed:
            raise ValidationError("自分自身をフォローすることはできません。")

    def __str__(self):
        return f"{self.following} follows {self.followed}"
