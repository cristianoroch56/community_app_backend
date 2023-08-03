from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import User
from authentication.models import ActivationOTP, ForgetPasswordOtp, ForgetPasswordToken

# Register your models here.
admin.site.register(ActivationOTP)
admin.site.register(ForgetPasswordOtp)


@admin.register(ForgetPasswordToken)
class ForgetPasswordTokenAdmin(admin.ModelAdmin):
    readonly_fields = ("token",)
    list_display = ["user", "token", "created_at"]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Customize the displayed fields, filters, etc. if needed
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "parent_id",
        "online",
        "country_code",
        "country_flag"
    ]
