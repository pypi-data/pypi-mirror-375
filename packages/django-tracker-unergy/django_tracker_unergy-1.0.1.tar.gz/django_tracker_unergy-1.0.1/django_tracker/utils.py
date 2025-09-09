import json
from typing import Any, Dict, List, Optional

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from .constants import SENSITIVE_FIELDS
from .middleware import get_current_user


class AuditDataSerializer:
    """Serializa datos para auditoría de forma segura"""

    @staticmethod
    def serialize_value(value: Any) -> str:
        """Serializa un valor a string de forma segura"""
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return str(value)

        if isinstance(value, models.Model):
            return f"{value.__class__.__name__}(id={value.pk})"

        try:
            return json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def mask_sensitive_data(field_name: str, value: Any) -> Any:
        """Enmascara datos sensibles"""
        if any(sensitive in field_name.lower() for sensitive in SENSITIVE_FIELDS):
            return "***MASKED***" if value else None
        return value

    @staticmethod
    def get_field_changes(
        old_instance: models.Model,
        new_instance: models.Model,
        tracked_fields: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Obtiene los cambios entre dos instancias"""
        changes = {}

        if not tracked_fields:
            tracked_fields = [f.name for f in new_instance._meta.fields]

        for field_name in tracked_fields:
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(new_instance, field_name, None)

            if old_value != new_value:
                changes[field_name] = {
                    "old_value": AuditDataSerializer.mask_sensitive_data(
                        field_name, AuditDataSerializer.serialize_value(old_value)
                    ),
                    "new_value": AuditDataSerializer.mask_sensitive_data(
                        field_name, AuditDataSerializer.serialize_value(new_value)
                    ),
                }

        return changes
    
    @staticmethod
    def get_combined_changes(
        old_instance: models.Model,
        new_instance: models.Model,
        tracked_fields: Optional[List[str]] = None,
        tracked_m2m_fields: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Obtiene cambios combinados de campos regulares y M2M"""
        # Obtener cambios de campos regulares
        field_changes = AuditDataSerializer.get_field_changes(
            old_instance, new_instance, tracked_fields
        )
        
        # Obtener cambios de campos M2M
        m2m_changes = M2MAuditUtils.get_m2m_changes(
            old_instance, new_instance, tracked_m2m_fields
        )
        
        # Combinar ambos tipos de cambios
        combined_changes = field_changes.copy()
        for field_name, m2m_change in m2m_changes.items():
            combined_changes[field_name] = {
                "change_type": "many_to_many",
                **m2m_change
            }
        
        return combined_changes


class M2MAuditUtils:
    """Utilidades para auditoría de relaciones Many-to-Many"""
    
    @staticmethod
    def get_m2m_field_names(instance: models.Model) -> List[str]:
        """Obtiene los nombres de todos los campos ManyToMany de un modelo"""
        return [
            field.name for field in instance._meta.get_fields()
            if isinstance(field, models.ManyToManyField)
        ]
    
    @staticmethod
    def get_m2m_changes(old_instance: models.Model, new_instance: models.Model, 
                       tracked_m2m_fields: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Detecta cambios en campos Many-to-Many entre dos instancias"""
        changes = {}
        
        # Si no se especifican campos M2M, obtener todos
        if tracked_m2m_fields is None:
            tracked_m2m_fields = M2MAuditUtils.get_m2m_field_names(new_instance)
        
        for field_name in tracked_m2m_fields:
            try:
                # Obtener los querysets de ambas instancias
                old_m2m = getattr(old_instance, field_name).all()
                new_m2m = getattr(new_instance, field_name).all()
                
                # Convertir a sets para comparación
                old_pks = set(old_m2m.values_list('pk', flat=True))
                new_pks = set(new_m2m.values_list('pk', flat=True))
                
                # Detectar elementos agregados y removidos
                added_pks = new_pks - old_pks
                removed_pks = old_pks - new_pks
                
                if added_pks or removed_pks:
                    # Obtener objetos completos para serialización
                    related_model = getattr(new_instance, field_name).model
                    
                    added_objects = list(related_model.objects.filter(pk__in=added_pks)) if added_pks else []
                    removed_objects = list(related_model.objects.filter(pk__in=removed_pks)) if removed_pks else []
                    
                    changes[field_name] = {
                        "added": [M2MAuditUtils._serialize_m2m_object(obj) for obj in added_objects],
                        "removed": [M2MAuditUtils._serialize_m2m_object(obj) for obj in removed_objects],
                        "old_count": len(old_pks),
                        "new_count": len(new_pks)
                    }
                    
            except Exception as e:
                # En caso de error, registrar el problema pero continuar
                import logging
                logger = logging.getLogger('django_tracker')
                logger.warning(f"Error detecting M2M changes for field {field_name}: {e}")
                
        return changes
    
    @staticmethod
    def _serialize_m2m_object(obj: models.Model) -> Dict[str, Any]:
        """Serializa un objeto relacionado para auditoría M2M"""
        return {
            "pk": obj.pk,
            "model": obj.__class__.__name__,
            "str_representation": str(obj)
        }
    
    @staticmethod
    def get_current_m2m_state(instance: models.Model, m2m_field_names: List[str]) -> Dict[str, List]:
        """Obtiene el estado actual de campos M2M para una instancia"""
        state = {}
        for field_name in m2m_field_names:
            try:
                m2m_manager = getattr(instance, field_name)
                objects = list(m2m_manager.all())
                state[field_name] = [M2MAuditUtils._serialize_m2m_object(obj) for obj in objects]
            except Exception:
                state[field_name] = []
        return state


class AuditUserExtractor:
    """Extrae información del usuario para auditoría"""

    @staticmethod
    def get_user_info(request=None) -> Dict[str, Any]:
        """Obtiene información del usuario actual"""

        user = get_current_user()

        return {
            "user_id": getattr(user, "id", None) if user else None,
            "username": getattr(user, "username", "anonymous") if user else "anonymous",
            "email": getattr(user, "email", None) if user else None,
        }
