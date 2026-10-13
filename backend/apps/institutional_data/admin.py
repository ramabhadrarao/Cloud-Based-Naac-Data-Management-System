from django.contrib import admin
from .models import (
    AcademicYear, DataElement, Department, EvidenceAsset, FactEvidenceLink,
    Framework, FrameworkCriterion, FrameworkEdition, FrameworkMetric,
    Institution, InstitutionMembership, InstitutionalFact, MetricDataMapping,
    Programme, ReportSnapshot,
)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "institution_type", "is_active")
    search_fields = ("code", "name")
    list_filter = ("institution_type", "is_active")


@admin.register(InstitutionMembership)
class InstitutionMembershipAdmin(admin.ModelAdmin):
    list_display = ("institution", "user", "role", "is_active")
    list_filter = ("institution", "role", "is_active")
    search_fields = ("user__username", "user__email", "institution__name")


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("institution", "label", "start_date", "end_date", "is_current")
    list_filter = ("institution", "is_current")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("institution", "code", "name", "is_active")
    list_filter = ("institution", "is_active")
    search_fields = ("code", "name")


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("department", "code", "name", "award_level", "is_active")
    list_filter = ("department__institution", "award_level", "is_active")
    search_fields = ("code", "name")


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "authority", "is_enabled", "is_system")
    list_filter = ("is_enabled", "is_system")
    search_fields = ("code", "name", "authority")


class FrameworkCriterionInline(admin.TabularInline):
    model = FrameworkCriterion
    extra = 0


@admin.register(FrameworkEdition)
class FrameworkEditionAdmin(admin.ModelAdmin):
    list_display = ("framework", "version", "status", "effective_from", "effective_to", "config_version")
    list_filter = ("framework", "status")
    search_fields = ("framework__name", "version", "title")


class FrameworkMetricInline(admin.TabularInline):
    model = FrameworkMetric
    extra = 0


@admin.register(FrameworkCriterion)
class FrameworkCriterionAdmin(admin.ModelAdmin):
    list_display = ("edition", "code", "title", "parent", "is_applicable", "sort_order")
    list_filter = ("edition__framework", "edition", "is_applicable")
    search_fields = ("code", "title", "description")
    inlines = [FrameworkMetricInline]


@admin.register(FrameworkMetric)
class FrameworkMetricAdmin(admin.ModelAdmin):
    list_display = ("criterion", "code", "title", "metric_type", "required", "is_applicable")
    list_filter = ("criterion__edition__framework", "metric_type", "required", "is_applicable")
    search_fields = ("code", "title", "definition")


@admin.register(DataElement)
class DataElementAdmin(admin.ModelAdmin):
    list_display = ("key", "label", "value_type", "default_unit", "sensitivity", "is_active")
    list_filter = ("value_type", "sensitivity", "is_active")
    search_fields = ("key", "label", "description")


@admin.register(InstitutionalFact)
class InstitutionalFactAdmin(admin.ModelAdmin):
    list_display = ("institution", "data_element", "academic_year", "scope_type", "scope_key", "status", "updated_at")
    list_filter = ("institution", "academic_year", "status", "scope_type", "data_element")
    search_fields = ("data_element__key", "scope_key", "source_system", "source_record_id")
    readonly_fields = ("created_at", "updated_at", "submitted_at", "verified_at", "approved_at")


@admin.register(EvidenceAsset)
class EvidenceAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "source_system", "version", "confidentiality", "uploaded_by", "uploaded_at")
    list_filter = ("institution", "confidentiality", "source_system")
    search_fields = ("title", "description", "sha256", "source_record_id")


@admin.register(FactEvidenceLink)
class FactEvidenceLinkAdmin(admin.ModelAdmin):
    list_display = ("fact", "evidence", "linked_by", "linked_at")
    list_filter = ("fact__institution",)


@admin.register(MetricDataMapping)
class MetricDataMappingAdmin(admin.ModelAdmin):
    list_display = ("metric", "data_element", "mapping_type", "mapping_code", "is_active", "reviewed_by")
    list_filter = ("metric__criterion__edition__framework", "mapping_type", "is_active")


@admin.register(ReportSnapshot)
class ReportSnapshotAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "edition", "academic_year", "status", "generated_by", "created_at")
    list_filter = ("institution", "edition__framework", "status", "academic_year")
    search_fields = ("title", "checksum")
    readonly_fields = ("created_at", "finalized_at", "checksum")
