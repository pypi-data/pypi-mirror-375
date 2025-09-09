from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "action",
        "level",
        "content_type",
        "object_id",
        "username",
        "ip_address",
    ]
    list_filter = ["action", "level", "content_type", "created_at"]
    search_fields = ["username", "user_email", "object_id"]
    readonly_fields = [
        "created_at",
        "content_type",
        "object_id",
        "action",
        "level",
        "changes",
        "user_id",
        "username",
        "user_email",
        "metadata",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = [
        (
            "Objeto Auditado",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Información de la Acción",
            {
                "fields": (
                    "action",
                    "level",
                    "changes",
                )
            },
        ),
        (
            "Usuario",
            {
                "fields": (
                    "user_id",
                    "username",
                    "user_email",
                )
            },
        ),
        (
            "Metadatos",
            {
                "fields": (
                    "metadata",
                    "created_at",
                )
            },
        ),
    ]
