import logging
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import GenericRelation

from .model_identifiers import instance_to_str
from .core import enforcer


logger = logging.getLogger(__name__)


class AddRemovePolicyMixin:
    """
    Mixin for adding and removing policies.

    Do not use this mixin directly, unless you know what you're doing.
    More likely than not, you should use one of the subclasses:
    AddRemovePermissionPolicyMixin or AddRemoveGroupingPolicyMixin.
    This is because the mixin does not define the function for adding and removing policies.
    """

    @property
    def policy_add_function(self):
        raise NotImplementedError("This needs to be implemented by each class")

    @property
    def policy_remove_function(self):
        raise NotImplementedError("This needs to be implemented by each class")

    @property
    def access_policy_identifiers(self):
        raise NotImplementedError("This needs to be implemented by each class")

    def add_access_permission_policy(self) -> bool:
        identifiers = self.access_policy_identifiers
        logger.debug(f"Adding a policy with {identifiers=}")
        return self.policy_add_function(*identifiers)

    def remove_access_permission_policy(self) -> bool:
        identifiers = self.access_policy_identifiers
        logger.debug(f"Removing a policy with {identifiers=}")
        return self.policy_remove_function(*identifiers)


class AddRemovePermissionPolicyMixin(AddRemovePolicyMixin):
    @property
    def policy_add_function(self):
        return enforcer.add_policy

    @property
    def policy_remove_function(self):
        return enforcer.remove_policy


class AddRemoveGroupingPolicyMixin(AddRemovePolicyMixin):
    @property
    def policy_add_function(self):
        return enforcer.add_grouping_policy

    @property
    def policy_remove_function(self):
        return enforcer.remove_grouping_policy


class PolicyLifecycleMixin(AddRemovePolicyMixin, models.Model):
    """
    Mixin that:
      - On create: adds policy after save.
      - On update: removes policy tied to the old instance, then adds policy for the new state.
      - On delete: removes policy, then deletes the row.

    Requirement on the concrete model is that it must inherit from either
    AddRemovePermissionPolicyMixin or AddRemoveGroupingPolicyMixin.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        old_instance = None
        is_update = self.pk is not None

        if is_update:
            try:
                # Get the old persisted state to remove its policy
                old_instance = self.__class__.objects.get(pk=self.pk)
            except ObjectDoesNotExist:
                logger.warning(
                    f"Object with {self.__class__.__name__=} and {self.pk=} had .save() method called on it, but it does not exist in the database."
                )
                """
                There has been an error, but it makes no sense, so we continue,
                most of the time it should not happen and the rest of the time
                it should not be an issue.
                """

        if old_instance is not None:
            # Remove policy based on the old state
            old_instance.remove_access_permission_policy()

        # Persist the new state
        super().save(*args, **kwargs)

        # Add policy based on the new state
        self.add_access_permission_policy()

    def delete(self, *args, **kwargs):
        # Remove policy based on current state before deleting
        self.remove_access_permission_policy()
        super().delete(*args, **kwargs)


class ObjectIdentifierMixin:
    @property
    def unique_object_instance_identifier(self) -> str:
        return instance_to_str(self)


class ResourceAccessPermissionMixin(models.Model):
    # standardize the relation name to `content_access_permission`
    content_access_permission = GenericRelation(
        "content_access_control.ContentAccessPermission",
        content_type_field="resource_content_type",
        object_id_field="resource_id",
        related_query_name="resource",
    )

    class Meta:
        abstract = True


class SubjectAccessPermissionMixin(models.Model):
    content_access_permission = GenericRelation(
        "content_access_control.ContentAccessPermission",
        content_type_field="subject_content_type",
        object_id_field="subject_id",
        related_query_name="subject",
    )

    class Meta:
        abstract = True
