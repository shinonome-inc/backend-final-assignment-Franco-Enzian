from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class Tweet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes_given")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [UniqueConstraint(fields=["tweet", "user"], name="OnlyOneLike")]

    def __str__(self):
        return f"{self.user}が{self.tweet.user}のツイートをいいねした：「{self.tweet.content}」"
