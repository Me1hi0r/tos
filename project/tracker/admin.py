from django.contrib import admin
from .models import UserLog, TrackedHost


@admin.register(UserLog)
class TosAdmin(admin.ModelAdmin):
    list_filter = ("host__host",)


@admin.register(TrackedHost)
class HostAdmin(admin.ModelAdmin):
    list_filter = ("active", )
    list_display = ("active", "host", "users_count", "medium_tos")

    @admin.display(description="users")
    def users_count(self, host):
        return UserLog.objects.filter(host=TrackedHost.objects.get(host=host)).count()

    @admin.display(description="medium tos")
    def medium_tos(self, host):
        logs = UserLog.objects.filter(host=TrackedHost.objects.get(host=host))
        return int(sum(logs.values_list('tos', flat=True)) / logs.count()) if logs else 0
