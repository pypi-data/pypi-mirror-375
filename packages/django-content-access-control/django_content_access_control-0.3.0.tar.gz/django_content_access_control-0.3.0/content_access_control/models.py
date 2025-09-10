from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from content_access_control.policy_mixins import (
    AddRemovePermissionPolicyMixin,
    AddRemoveGroupingPolicyMixin,
    PolicyLifecycleMixin,
    ObjectIdentifierMixin,
    SubjectAccessPermissionMixin,
    ResourceAccessPermissionMixin,
)


class ExpectedModel(ObjectIdentifierMixin, models.Model):
    class Meta:
        abstract = True


class CasbinRule(models.Model):
    ptype = models.CharField(max_length=255)
    v0 = models.CharField(max_length=255, blank=True)
    v1 = models.CharField(max_length=255, blank=True)
    v2 = models.CharField(max_length=255, blank=True)
    v3 = models.CharField(max_length=255, blank=True)
    v4 = models.CharField(max_length=255, blank=True)
    v5 = models.CharField(max_length=255, blank=True)

    def __str__(self):
        text = self.ptype

        if self.v0:
            text = text + ", " + self.v0
        if self.v1:
            text = text + ", " + self.v1
        if self.v2:
            text = text + ", " + self.v2
        if self.v3:
            text = text + ", " + self.v3
        if self.v4:
            text = text + ", " + self.v4
        if self.v5:
            text = text + ", " + self.v5
        return text

    def __repr__(self):
        return '<CasbinRule {}: "{}">'.format(self.id, str(self))


class ContentAccessPermission(
    PolicyLifecycleMixin, AddRemovePermissionPolicyMixin, models.Model
):
    """
    Model used to encapsulate a generic link between
    "which *subject* can do which *action* on which *resource*"
    """

    subject_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="subject_type"
    )
    subject_id = models.PositiveIntegerField()
    subject = GenericForeignKey("subject_content_type", "subject_id")
    resource_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="resource_type"
    )
    resource_id = models.PositiveIntegerField()
    resource = GenericForeignKey("resource_content_type", "resource_id")
    action = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subject_content_type",
                    "subject_id",
                    "resource_content_type",
                    "resource_id",
                    "action",
                ],
                name="unique_subject_resource",
            )
        ]

    @property
    def access_policy_identifiers(self):
        return (
            get_uuid_of_model(self.subject),
            get_uuid_of_model(self.resource),
            self.action,
        )

    def __str__(self):
        # Use ContentType to avoid accessing the actual related objects
        try:
            sub_app_label = self.subject_content_type.app_label
            sub_model = self.subject_content_type.model
            sub_label = f"{sub_app_label}.{sub_model}"
        except Exception:
            sub_label = "unknown.subject"

        try:
            res_app_label = self.resource_content_type.app_label
            res_model = self.resource_content_type.model
            res_label = f"{res_app_label}.{res_model}"
        except Exception:
            res_label = "unknown.resource"

        # Prefer IDs to avoid fetching GenericForeignKey instances.
        # If you still want best-effort human-readable names without hard failures,
        # you can try to use str(self.subject) / str(self.resource) guarded by try/except.
        return f'{sub_label}({self.subject_id}) can do: "{self.action}" on {res_label}({self.resource_id})'


class PolicySubject(
    SubjectAccessPermissionMixin,
    PolicyLifecycleMixin,
    AddRemoveGroupingPolicyMixin,
    ObjectIdentifierMixin,
    models.Model,
):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="default")

    @property
    def access_policy_identifiers(self):
        return (self.user.username, self.unique_object_instance_identifier)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PolicySubjectGroup(
    SubjectAccessPermissionMixin,
    AddRemoveGroupingPolicyMixin,
    ObjectIdentifierMixin,
    models.Model,
):
    name = models.CharField(max_length=255)
    parent_group = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def access_policy_identifiers(self):
        return (
            self.unique_object_instance_identifier,
            self.parent_group.unique_object_instance_identifier,
        )

    def __str__(self):
        parent = str(self.parent_group or "")
        SEP = " - " if parent else ""
        return f"{parent}{SEP}{self.name}"

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if not self.parent_group:
            return
        self.remove_access_permission_policy()

    def save(self, *args, **kwargs):
        if self.pk:
            # Check if not self-referential
            if self.parent_network_id == self.pk:
                raise ValueError(
                    "Network parent cannot reference the network itself, choose different parent or set to null"
                )

            # Delete the old grouping policy
            old_instance = PolicySubjectGroup.objects.get(pk=self.pk)
            if old_instance.parent_network:
                old_instance.remove_access_permission_policy()

        super().save(*args, **kwargs)
        if not self.parent_group:
            return
        self.add_access_permission_policy()


class SubjectToGroup(
    PolicyLifecycleMixin,
    AddRemoveGroupingPolicyMixin,
    ObjectIdentifierMixin,
    models.Model,
):
    subject = models.ForeignKey(PolicySubject, on_delete=models.CASCADE)
    subject_group = models.ForeignKey(PolicySubjectGroup, on_delete=models.CASCADE)

    @property
    def access_policy_identifiers(self):
        return (
            self.subject.unique_object_instance_identifier,
            self.subject_group.unique_object_instance_identifier,
        )

    def __str__(self):
        return f'Subject: "{self.subject}", assigned to: "{self.subject_group}"'


ModelType = models.Model | ExpectedModel


def get_uuid_of_model(model_instance: ModelType):
    if hasattr(model_instance, "unique_object_instance_identifier"):
        return model_instance.unique_object_instance_identifier
    return str(model_instance)


class Feature(
    ResourceAccessPermissionMixin,
    ObjectIdentifierMixin,
    models.Model,
):
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="unique_feature_name_constraint"
            )
        ]

    def __str__(self):
        return self.name
