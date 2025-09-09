from django.apps import AppConfig


class ContentAccessControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_content_access_control"

    def ready(self):
        from django.conf import settings  # noqa

        load_eager = getattr(settings, "CONTENT_ACCESS_CONTROL_LOAD_EAGER", False)
        if load_eager:
            from .core import enforcer  # noqa

            enforcer._load()
