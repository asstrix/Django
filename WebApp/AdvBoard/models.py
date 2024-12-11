from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    advertisements_count = models.PositiveIntegerField(default=0)

class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    photo1 = models.BinaryField(blank=True, null=True)
    photo2 = models.BinaryField(blank=True, null=True)
    photo3 = models.BinaryField(blank=True, null=True)
    photo4 = models.BinaryField(blank=True, null=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_ads", blank=True)
    dislikes = models.ManyToManyField(CustomUser, related_name="disliked_ads",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    advertisement = models.ForeignKey(Advertisement, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.advertisement}'