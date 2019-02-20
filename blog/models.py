from django.db import models
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    text = models.TextField()
    price = models.FloatField(
        validators=[MinValueValidator(0.1)])
    deadline_date = models.DateTimeField(
        blank=True, null=True)
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)
    is_banned = models.BooleanField(default=False, editable=False)
    version = models.IntegerField(editable=False, default=0)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Bid(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    bid = models.CharField(max_length=20)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
