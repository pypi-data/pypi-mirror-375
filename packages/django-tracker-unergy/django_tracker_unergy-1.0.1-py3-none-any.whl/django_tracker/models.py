from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .constants import AuditAction, AuditLevel
from .managers import AuditLogManager


class AuditLog(models.Model):
    """Modelo principal de auditoría con mayor flexibilidad"""

    # Relación genérica al objeto auditado
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="tracker_logs",
        verbose_name="Content Type",
        help_text="Tipo de contenido del objeto auditado",
    )
    object_id = models.PositiveIntegerField(
        verbose_name="Object ID", db_index=True, help_text="ID del objeto auditado"
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Información de la acción
    action = models.CharField(
        max_length=10,
        choices=AuditAction.choices,
        default=AuditAction.UPDATE,
        verbose_name="Action",
        help_text="Tipo de acción realizada",
    )
    level = models.CharField(
        max_length=10,
        choices=AuditLevel.choices,
        default=AuditLevel.MEDIUM,
        verbose_name="Level",
        help_text="Nivel de importancia del log",
    )

    # Cambios realizados (JSON)
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cambios realizados en el objeto",
        verbose_name="Changes",
    )

    # Información del usuario
    user_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="ID del usuario que realizó la acción",
        verbose_name="User ID",
    )
    username = models.CharField(
        max_length=150,
        default="anonymous",
        verbose_name="Username",
        help_text="Nombre de usuario que realizó la acción",
    )
    user_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="User Email",
        help_text="Email del usuario que realizó la acción",
    )

    # Metadatos adicionales
    metadata = models.JSONField(default=dict, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    # Manager personalizado
    objects = AuditLogManager()

    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user_id", "username"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.content_type.model}({self.object_id}) by {self.username}"
