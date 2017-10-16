from django.contrib import admin
from .models import Plan, Profile, Site, PlanHistory

@admin.register(Plan)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Site)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(PlanHistory)
class UserAdmin(admin.ModelAdmin):
    pass
