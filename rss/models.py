from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from register.models import Site

class Article(models.Model):
    class Meta:
        db_table = 'articles'
    title = models.CharField("タイトル", max_length=255)
    url = models.URLField()
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    judged_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user.id) + ': ' + self.title
