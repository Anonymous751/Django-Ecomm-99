from django.contrib import admin
from apps.accounts.models import CustomUser
from django.contrib.auth.admin import UserAdmin


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_private",
        "is_blocked",
        "two_factor_enabled",
        "dark_mode",
    )
    list_editable = ("two_factor_enabled", "is_private", "is_blocked", "dark_mode")
    list_filter = ("two_factor_enabled", "is_private", "is_blocked", "dark_mode")
    search_fields = ("username", "email")