import logging

from rest_framework.permissions import BasePermission
from .core import enforcer


logger = logging.getLogger(__name__)


class SubjectHasUrlPermission(BasePermission):
    """
    Custom DRF permission class using dauthz to enforce URL-based access control.
    """

    def has_permission(self, request, view):
        if hasattr(request, "policy_subject"):
            subject = request.policy_subject.unique_object_instance_identifier
        else:
            if hasattr(request, "user"):
                subject = str(request.user.username)
            else:
                subject = "anonymous"
        resource = request.path
        action = request.method
        can_access = enforcer.enforce(subject, resource, action)
        logger.debug(
            f"Verified access for {resource}, and {action=}, and {subject=} --> Result: {can_access}"
        )
        return can_access
