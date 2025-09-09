from typing import Dict, List, Optional

from django.db import models

from .constants import DEFAULT_EXCLUDED_FIELDS, AuditAction, AuditLevel, AUDITED_M2M_ACTIONS, DEFAULT_M2M_METADATA
from .models import AuditLog
from .utils import AuditDataSerializer, M2MAuditUtils


class AuditService:
    """Servicio principal para manejo de auditoría"""

    @staticmethod
    def audit_create(
        instance: models.Model,
        excluded_fields: Optional[List[str]] = None,
        level: str = AuditLevel.MEDIUM,
        metadata: Optional[Dict] = None,
    ):
        """Audita la creación de un objeto"""

        # Obtener valores iniciales
        excluded = excluded_fields or DEFAULT_EXCLUDED_FIELDS
        initial_data = {}

        for field in instance._meta.fields:
            if field.name not in excluded:
                value = getattr(instance, field.name, None)
                if value is not None:
                    initial_data[field.name] = {
                        "old_value": None,
                        "new_value": AuditDataSerializer.mask_sensitive_data(
                            field.name, AuditDataSerializer.serialize_value(value)
                        ),
                    }

        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.CREATE,
            changes=initial_data,
            level=level,
            metadata=metadata or {},
        )

    @staticmethod
    def audit_update(
        old_instance: models.Model,
        new_instance: models.Model,
        tracked_fields: Optional[List[str]] = None,
        tracked_m2m_fields: Optional[List[str]] = None,
        excluded_fields: Optional[List[str]] = None,
        level: str = AuditLevel.MEDIUM,
        metadata: Optional[Dict] = None,
    ):
        """Audita la actualización de un objeto incluyendo campos M2M"""
        excluded = excluded_fields or DEFAULT_EXCLUDED_FIELDS

        if tracked_fields:
            # Filtrar campos excluidos de los campos trackeados
            tracked_fields = [f for f in tracked_fields if f not in excluded]
        else:
            # Usar todos los campos regulares excepto los excluidos
            tracked_fields = [
                f.name for f in new_instance._meta.fields if f.name not in excluded
            ]

        # Usar método combinado para obtener cambios regulares y M2M
        changes = AuditDataSerializer.get_combined_changes(
            old_instance, new_instance, tracked_fields, tracked_m2m_fields
        )

        if changes:  # Solo crear log si hay cambios
            return AuditLog.objects.create_audit(
                instance=new_instance,
                action=AuditAction.UPDATE,
                changes=changes,
                level=level,
                metadata=metadata or {},
            )

        return None

    @staticmethod
    def audit_delete(
        instance: models.Model,
        level: str = AuditLevel.HIGH,
        metadata: Optional[Dict] = None,
    ):
        """Audita la eliminación de un objeto"""
        # Capturar estado final antes de eliminar
        final_state = {}
        for field in instance._meta.fields:
            if field.name not in DEFAULT_EXCLUDED_FIELDS:
                value = getattr(instance, field.name, None)
                if value is not None:
                    final_state[field.name] = {
                        "old_value": AuditDataSerializer.mask_sensitive_data(
                            field.name, AuditDataSerializer.serialize_value(value)
                        ),
                        "new_value": None,
                    }

        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.DELETE,
            changes=final_state,
            level=level,
            metadata=metadata or {},
        )

    @staticmethod
    def audit_read(
        instance: models.Model,
        level: str = AuditLevel.LOW,
        metadata: Optional[Dict] = None,
    ):
        """Audita la lectura/consulta de un objeto"""
        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.READ,
            changes={},
            level=level,
            metadata=metadata or {},
        )
    
    @staticmethod
    def audit_m2m_change(
        instance: models.Model,
        field_name: str,
        action: str,  # 'pre_add', 'post_add', 'pre_remove', 'post_remove', 'pre_clear', 'post_clear'
        pk_set: Optional[set] = None,
        level: str = AuditLevel.MEDIUM,
        metadata: Optional[Dict] = None,
    ):
        """Audita cambios específicos en relaciones M2M usando señales"""
        
        # Obtener el modelo relacionado
        m2m_field = instance._meta.get_field(field_name)
        related_model = m2m_field.related_model
        
        # Crear información del cambio
        m2m_change_info = {
            "field_name": field_name,
            "action": action,
            "related_model": related_model.__name__,
        }
        
        if pk_set:
            # Obtener objetos relacionados para información adicional
            related_objects = related_model.objects.filter(pk__in=pk_set)
            m2m_change_info["affected_objects"] = [
                M2MAuditUtils._serialize_m2m_object(obj) for obj in related_objects
            ]
            m2m_change_info["affected_count"] = len(pk_set)
        
        changes = {
            field_name: {
                "change_type": "many_to_many_signal",
                **m2m_change_info
            }
        }
        
        # Combinar metadatos por defecto con los proporcionados
        combined_metadata = DEFAULT_M2M_METADATA.copy()
        combined_metadata.update(metadata or {})
        
        return AuditLog.objects.create_audit(
            instance=instance,
            action=AuditAction.UPDATE,
            changes=changes,
            level=level,
            metadata=combined_metadata,
        )


class AuditConfig:
    """Configuración de auditoría para modelos"""

    def __init__(
        self,
        tracked_fields: Optional[List[str]] = None,
        tracked_m2m_fields: Optional[List[str]] = None,
        excluded_fields: Optional[List[str]] = None,
        audit_creates: bool = True,
        audit_updates: bool = True,
        audit_deletes: bool = True,
        audit_reads: bool = False,
        audit_m2m_changes: bool = True,
        level: str = AuditLevel.MEDIUM,
    ):
        self.tracked_fields = tracked_fields
        self.tracked_m2m_fields = tracked_m2m_fields
        self.excluded_fields = excluded_fields or []
        self.audit_creates = audit_creates
        self.audit_updates = audit_updates
        self.audit_deletes = audit_deletes
        self.audit_reads = audit_reads
        self.audit_m2m_changes = audit_m2m_changes
        self.level = level
