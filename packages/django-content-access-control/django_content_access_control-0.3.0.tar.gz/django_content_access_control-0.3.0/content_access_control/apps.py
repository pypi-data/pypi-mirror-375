from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class ContentAccessControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content_access_control"

    def ready(self):
        from django.conf import settings  # noqa
        from .core import enforcer  # noqa

        try:
            getattr(settings, "CASBIN_MODEL")
        except AttributeError:
            raise ImproperlyConfigured("CASBIN_MODEL must be set in settings.py")

        enforcer._load()
