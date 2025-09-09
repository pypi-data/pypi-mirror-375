from functools import wraps
from typing import List, Optional

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .constants import AuditLevel, AUDITED_M2M_ACTIONS
from .middleware import get_current_user
from .services import AuditConfig, AuditService


def auditable(
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
    """
    Decorator mejorado para auditoría de modelos incluyendo soporte M2M

    Args:
        tracked_fields: Lista de campos específicos a trackear
        tracked_m2m_fields: Lista de campos ManyToMany específicos a trackear
        excluded_fields: Lista de campos a excluir del tracking
        audit_creates: Si auditar creaciones
        audit_updates: Si auditar actualizaciones
        audit_deletes: Si auditar eliminaciones
        audit_reads: Si auditar lecturas
        audit_m2m_changes: Si auditar cambios en relaciones ManyToMany
        level: Nivel de auditoría
    """

    def decorator(cls):
        if not issubclass(cls, models.Model):
            raise ValueError(
                "El decorator auditable solo puede aplicarse a modelos Django"
            )

        # Configuración de auditoría
        audit_config = AuditConfig(
            tracked_fields=tracked_fields,
            tracked_m2m_fields=tracked_m2m_fields,
            excluded_fields=excluded_fields,
            audit_creates=audit_creates,
            audit_updates=audit_updates,
            audit_deletes=audit_deletes,
            audit_reads=audit_reads,
            audit_m2m_changes=audit_m2m_changes,
            level=level,
        )

        # Guardar configuración en el modelo
        cls._audit_config = audit_config

        # Interceptar save
        if audit_config.audit_creates or audit_config.audit_updates:
            original_save = cls.save

            @wraps(original_save)
            def new_save(self, *args, **kwargs):
                is_creation = self.pk is None
                old_instance = None

                if not is_creation and audit_config.audit_updates:
                    try:
                        old_instance = cls.objects.get(pk=self.pk)
                    except cls.DoesNotExist:
                        old_instance = None

                # Ejecutar save original
                result = original_save(self, *args, **kwargs)
                if is_creation and audit_config.audit_creates:
                    AuditService.audit_create(
                        instance=self,
                        excluded_fields=audit_config.excluded_fields,
                        level=audit_config.level,
                    )
                elif old_instance and audit_config.audit_updates:
                    AuditService.audit_update(
                        old_instance=old_instance,
                        new_instance=self,
                        tracked_fields=audit_config.tracked_fields,
                        tracked_m2m_fields=audit_config.tracked_m2m_fields,
                        excluded_fields=audit_config.excluded_fields,
                        level=audit_config.level,
                    )
                return result

            cls.save = new_save

        # Interceptar delete
        if audit_config.audit_deletes:
            original_delete = cls.delete

            @wraps(original_delete)
            def new_delete(self, *args, **kwargs):
                AuditService.audit_delete(instance=self, level=audit_config.level)
                return original_delete(self, *args, **kwargs)

            cls.delete = new_delete
        
        # Configurar señales M2M si está habilitado
        if audit_config.audit_m2m_changes:
            _setup_m2m_signals(cls, audit_config)

        return cls

    return decorator


def _setup_m2m_signals(model_class, audit_config: AuditConfig):
    """Configura señales M2M para un modelo"""
    from .utils import M2MAuditUtils
    
    # Obtener campos M2M del modelo
    m2m_fields = M2MAuditUtils.get_m2m_field_names(model_class())
    
    # Filtrar por campos trackeados si se especifican
    if audit_config.tracked_m2m_fields:
        m2m_fields = [f for f in m2m_fields if f in audit_config.tracked_m2m_fields]
    
    for field_name in m2m_fields:
        field = model_class._meta.get_field(field_name)
        
        # Crear receptor de señal para este campo específico
        def create_m2m_handler(field_name):
            def handle_m2m_change(sender, instance, action, pk_set, **kwargs):
                # Solo auditar acciones que representen cambios reales
                if action in AUDITED_M2M_ACTIONS:
                    try:
                        AuditService.audit_m2m_change(
                            instance=instance,
                            field_name=field_name,
                            action=action,
                            pk_set=pk_set,
                            level=audit_config.level,
                        )
                    except Exception as e:
                        import logging
                        logger = logging.getLogger('django_tracker')
                        logger.error(f"Error auditing M2M change: {e}")
            return handle_m2m_change
        
        # Conectar la señal
        m2m_changed.connect(
            create_m2m_handler(field_name),
            sender=field.through,
            dispatch_uid=f"{model_class.__name__}_{field_name}_audit"
        )


# Decorator legacy para compatibilidad
def legacy_auditable(fields_to_track=None):
    """Decorator legacy mantenido para compatibilidad hacia atrás"""
    from .models import AttributeAudit

    def decorator(cls):
        original_save = cls.save

        @wraps(original_save)
        def new_save(self, *args, **kwargs):
            if self.pk:
                try:
                    old_obj = cls.objects.get(pk=self.pk)
                    campos = fields_to_track or [f.name for f in self._meta.fields]

                    for campo in campos:
                        old_value = getattr(old_obj, campo, None)
                        new_value = getattr(self, campo, None)

                        # Evitar ruido con campos de timestamp
                        if campo in ["created", "modified", "updated_at"]:
                            continue

                        if old_value != new_value:
                            AttributeAudit.objects.create(
                                model_name=self.__class__.__name__,
                                object_id=self.pk,
                                field_name=campo,
                                old_value=old_value,
                                new_value=new_value,
                                changed_by=get_current_user(),
                            )
                except Exception as e:
                    import logging

                    logger = logging.getLogger("auditlog")
                    logger.error(f"Error en auditoría legacy: {e}")

            return original_save(self, *args, **kwargs)

        cls.save = new_save
        return cls

    return decorator
