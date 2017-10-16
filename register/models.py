from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Plan(models.Model):
    class Meta:
        db_table = 'plans'
    name = models.CharField(max_length=50)
    limit = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

class Profile(models.Model):
    class Meta:
        db_table = 'profiles'
    plan = models.ForeignKey(Plan)
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.OneToOneField(User, related_name="profile")
    def __str__(self):
        return self.user.username

class Site(models.Model):
    class Meta:
        db_table = "sites"
    name = models.CharField(max_length=255, null=True)
    url = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='site', on_delete=models.CASCADE)
    judged_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

class PlanHistory(models.Model):
    class Meta:
        db_table = 'plans_history'
    user = models.ForeignKey(User)
    plan = models.ForeignKey(Plan)
    created_at = models.DateTimeField(default=timezone.now)
