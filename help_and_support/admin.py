from django.contrib import admin
from help_and_support.models import HelpAndSupport


class HelpAndSupportAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "created_at")

    def user_name(self, obj):
        return obj.user.username

    user_name.short_description = "User Name"

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "User Email"

    readonly_fields = ("user_name", "user_email")


admin.site.register(HelpAndSupport, HelpAndSupportAdmin)
