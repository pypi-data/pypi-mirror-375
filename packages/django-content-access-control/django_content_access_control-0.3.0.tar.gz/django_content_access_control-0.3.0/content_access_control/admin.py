from django.contrib import admin

from .models import (
    CasbinRule,
    Feature,
    PolicySubject,
    PolicySubjectGroup,
    SubjectToGroup,
)
from .admin_permission import register_permission_admin


class SubjectToGroupInline(admin.TabularInline):
    model = SubjectToGroup
    extra = 0


@admin.register(CasbinRule)
class CasbinRuleAdmin(admin.ModelAdmin): ...


@admin.register(PolicySubject)
class PolicySubjectAdmin(admin.ModelAdmin):
    inlines = [SubjectToGroupInline]


@admin.register(PolicySubjectGroup)
class PolicySubjectGroupAdmin(admin.ModelAdmin):
    inlines = [SubjectToGroupInline]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin): ...


register_permission_admin(Feature, ["access"])
