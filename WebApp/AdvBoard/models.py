from django.db import models
from django.contrib.auth.models import User


class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo1 = models.BinaryField(blank=True, null=True)
    photo2 = models.BinaryField(blank=True, null=True)
    photo3 = models.BinaryField(blank=True, null=True)
    photo4 = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    advertisement = models.ForeignKey(Advertisement, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.advertisement}'
