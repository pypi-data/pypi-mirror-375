# Django Tracker

Django Tracker is a middleware for Django that automatically audits and logs all model changes made through user requests. It records the user responsible, the fields changed, and other useful information for tracking data changes.

## Installation

```bash
pip install django-tracker-unergy
```

## Setup

1. Add `'django_tracker'` to `INSTALLED_APPS` in your `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_tracker',
]
```
and add the middleware
```python
MIDDLEWARE = [
    # ...
    'django_tracker.middleware.CurrentUserMiddleware'
]
```

2. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate django_tracker
```

## Usage

### Auditable Decorator

```python
from django_tracker.decorators import auditable
from django_tracker.constants import AuditLevel

@auditable(
    tracked_fields=['field1', 'field2'],
    tracked_m2m_fields=['categories', 'tags'],  # NEW: Track M2M fields
    excluded_fields=["created_at", "updated_at"],
    audit_creates=True,
    audit_updates=True,
    audit_deletes=True,
    audit_m2m_changes=True,  # NEW: Enable M2M tracking
    level=AuditLevel.MEDIUM
)
class MyModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()
    
    # Many-to-Many relationships that will be tracked
    categories = models.ManyToManyField('Category', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
```

### Many-to-Many Field Tracking

Django-tracker now supports automatic tracking of Many-to-Many field changes:

**Features:**
- Automatic detection of M2M additions, removals, and clears
- Detailed logging of affected objects with their string representations
- Signal-based tracking for real-time M2M changes
- Configurable M2M field selection
- Compatible with existing field tracking

**M2M Log Structure:**
```json
{
    "categories": {
        "change_type": "many_to_many_signal",
        "field_name": "categories",
        "action": "post_add",
        "related_model": "Category",
        "affected_objects": [
            {"pk": 1, "model": "Category", "str_representation": "Technology"},
            {"pk": 2, "model": "Category", "str_representation": "Django"}
        ],
        "affected_count": 2
    }
}
```

### Querying Audit Logs

You can view audit logs in the Django admin or directly from the model:

```python
from django_tracker.models import AuditLog

# Get changes for a specific object
logs = AuditLog.objects.filter(
    content_type__model='mymodel',
    object_id=obj_id
)

# Get changes by user
logs = AuditLog.objects.filter(username='username')

# Get M2M changes specifically
m2m_logs = AuditLog.objects.filter(
    changes__has_key='categories'  # PostgreSQL
)

# Get specific M2M actions
add_logs = AuditLog.objects.filter(
    changes__categories__action='post_add'
)
```

## License

MIT License. See LICENSE file for details.
