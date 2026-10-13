from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Institution(models.Model):
    """An institution using the platform; shared facts are scoped to one institution."""
    code = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=255)
    institution_type = models.CharField(max_length=80, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class InstitutionMembership(models.Model):
    """Maps an authenticated platform user to an institution and role."""
    class Role(models.TextChoices):
        INSTITUTION_ADMIN = "institution_admin", "Institution administrator"
        PRINCIPAL = "principal", "Principal / Director"
        IQAC_COORDINATOR = "iqac_coordinator", "IQAC coordinator"
        FRAMEWORK_COORDINATOR = "framework_coordinator", "Framework coordinator"
        HOD = "hod", "Head of department"
        DATA_OWNER = "data_owner", "Data owner"
        REVIEWER = "reviewer", "Reviewer"
        AUDITOR = "auditor", "Auditor"
        READ_ONLY = "read_only", "Read-only"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="institution_memberships")
    role = models.CharField(max_length=32, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["institution", "user"], name="uniq_inst_membership_user")
        ]
        indexes = [models.Index(fields=["user", "is_active"])]

    def __str__(self):
        return f"{self.user} · {self.institution} · {self.role}"


class AcademicYear(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="academic_years")
    label = models.CharField(max_length=20, help_text="Example: 2026-27")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(fields=["institution", "label"], name="uniq_inst_academic_year"),
            models.CheckConstraint(condition=Q(end_date__gte=models.F("start_date")), name="academic_year_date_order"),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must not be earlier than start date."})

    def __str__(self):
        return f"{self.institution.code} · {self.label}"


class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="departments")
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["institution", "code"], name="uniq_inst_department_code")
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Programme(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="programmes")
    code = models.CharField(max_length=60)
    name = models.CharField(max_length=255)
    award_level = models.CharField(max_length=80, blank=True)
    duration_years = models.PositiveSmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["department", "code"], name="uniq_dept_programme_code")
        ]

    @property
    def institution(self):
        return self.department.institution

    def __str__(self):
        return f"{self.code} — {self.name}"


class Framework(models.Model):
    """Stable framework identity; editions hold the versioned rules."""
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    authority = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=True)
    is_system = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code.upper()} — {self.name}"


class FrameworkEdition(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEWED = "reviewed", "Reviewed"
        ACTIVE = "active", "Active"
        RETIRED = "retired", "Retired"

    framework = models.ForeignKey(Framework, on_delete=models.PROTECT, related_name="editions")
    version = models.CharField(max_length=80, help_text="Authority edition / reporting cycle identifier")
    title = models.CharField(max_length=255, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    applicability = models.JSONField(default=dict, blank=True, help_text="Reviewed rules for institution/programme categories.")
    source_url = models.URLField(blank=True)
    source_checked_at = models.DateTimeField(null=True, blank=True)
    config_version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["framework__name", "-effective_from", "version"]
        constraints = [
            models.UniqueConstraint(fields=["framework", "version"], name="uniq_framework_edition_version")
        ]

    def clean(self):
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError({"effective_to": "Effective-to date must not precede effective-from date."})

    def __str__(self):
        return f"{self.framework.code.upper()} {self.version}"


class FrameworkCriterion(models.Model):
    edition = models.ForeignKey(FrameworkEdition, on_delete=models.CASCADE, related_name="criteria")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    code = models.CharField(max_length=80)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    guidance = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_applicable = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "code"]
        constraints = [
            models.UniqueConstraint(fields=["edition", "code"], name="uniq_edition_criterion_code")
        ]

    def __str__(self):
        return f"{self.edition} · {self.code} · {self.title}"


class FrameworkMetric(models.Model):
    class MetricType(models.TextChoices):
        NUMERIC = "numeric", "Numeric"
        TEXT = "text", "Text / narrative"
        BOOLEAN = "boolean", "Yes / no"
        TABLE = "table", "Structured table"
        EVIDENCE = "evidence", "Evidence checklist"
        OBE = "obe", "Outcome-based education"

    criterion = models.ForeignKey(FrameworkCriterion, on_delete=models.CASCADE, related_name="metrics")
    code = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    definition = models.TextField(blank=True)
    metric_type = models.CharField(max_length=16, choices=MetricType.choices, default=MetricType.TEXT)
    unit = models.CharField(max_length=60, blank=True)
    required = models.BooleanField(default=True)
    formula_spec = models.JSONField(default=dict, blank=True, help_text="Version-controlled, reviewed calculation specification.")
    validation_spec = models.JSONField(default=dict, blank=True)
    output_spec = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_applicable = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "code"]
        constraints = [
            models.UniqueConstraint(fields=["criterion", "code"], name="uniq_criterion_metric_code")
        ]

    def __str__(self):
        return f"{self.criterion.code} · {self.code}"


class DataElement(models.Model):
    """Canonical, framework-neutral definition for a reusable institutional fact."""
    class ValueType(models.TextChoices):
        TEXT = "text", "Text"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"
        RECORD = "record", "Structured record"
        RECORD_SET = "record_set", "Set of records"

    key = models.CharField(max_length=160, unique=True, help_text="Stable key, e.g. faculty.full_time_count")
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    value_type = models.CharField(max_length=16, choices=ValueType.choices, default=ValueType.TEXT)
    default_unit = models.CharField(max_length=60, blank=True)
    scope_policy = models.JSONField(default=dict, blank=True, help_text="Allowed scopes and required context.")
    validation_spec = models.JSONField(default=dict, blank=True)
    sensitivity = models.CharField(max_length=32, default="internal")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} — {self.label}"


class InstitutionalFact(models.Model):
    """Versionable value, tied to an institution, period, scope, provenance and approval state."""
    class ScopeType(models.TextChoices):
        INSTITUTION = "institution", "Institution"
        CAMPUS = "campus", "Campus"
        DEPARTMENT = "department", "Department"
        PROGRAMME = "programme", "Programme"
        COHORT = "cohort", "Student cohort"
        PERSON = "person", "Person"
        FACILITY = "facility", "Facility"
        ACTIVITY = "activity", "Activity"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        IN_REVIEW = "in_review", "In review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SUPERSEDED = "superseded", "Superseded"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="facts")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, null=True, blank=True, related_name="facts")
    data_element = models.ForeignKey(DataElement, on_delete=models.PROTECT, related_name="facts")
    scope_type = models.CharField(max_length=20, choices=ScopeType.choices, default=ScopeType.INSTITUTION)
    scope_key = models.CharField(max_length=160, blank=True, help_text="Stable scope identifier (e.g. department code or programme code).")
    value = models.JSONField()
    unit = models.CharField(max_length=60, blank=True)
    source_system = models.CharField(max_length=120, blank=True)
    source_record_id = models.CharField(max_length=160, blank=True)
    definition_version = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_institutional_facts")
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_institutional_facts")
    verified_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_institutional_facts")
    approved_at = models.DateTimeField(null=True, blank=True)
    supersedes = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="superseded_by")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_institutional_facts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["institution", "academic_year", "status"]),
            models.Index(fields=["data_element", "scope_type", "scope_key"]),
        ]

    def clean(self):
        errors = {}
        if self.academic_year_id and self.institution_id and self.academic_year.institution_id != self.institution_id:
            errors["academic_year"] = "Academic year must belong to the same institution."
        if self.supersedes_id and self.supersedes.institution_id != self.institution_id:
            errors["supersedes"] = "A fact can only supersede another fact from the same institution."
        if self.status == self.Status.APPROVED and not self.approved_by_id:
            errors["approved_by"] = "Approved facts must identify the approving user."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        period = self.academic_year.label if self.academic_year_id else "no academic year"
        return f"{self.institution.code} · {self.data_element.key} · {period}"


class EvidenceAsset(models.Model):
    class Confidentiality(models.TextChoices):
        PUBLIC = "public", "Public"
        INTERNAL = "internal", "Internal"
        CONFIDENTIAL = "confidential", "Confidential"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="evidence_assets")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    storage_key = models.CharField(max_length=500, blank=True, help_text="Object-storage key; do not store file bytes in this column.")
    external_url = models.URLField(blank=True)
    source_system = models.CharField(max_length=120, blank=True)
    source_record_id = models.CharField(max_length=160, blank=True, help_text="Optional identifier for an existing source document record.")
    sha256 = models.CharField(max_length=64, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    confidentiality = models.CharField(max_length=16, choices=Confidentiality.choices, default=Confidentiality.INTERNAL)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_evidence_assets")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    supersedes = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="superseded_by")

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["institution", "sha256"])]

    def clean(self):
        if self.supersedes_id and self.supersedes.institution_id != self.institution_id:
            raise ValidationError({"supersedes": "Evidence can only supersede evidence from the same institution."})
        if not self.storage_key and not self.external_url and not self.source_record_id:
            raise ValidationError("Provide a storage key, external URL, or source record reference.")

    def __str__(self):
        return self.title


class FactEvidenceLink(models.Model):
    fact = models.ForeignKey(InstitutionalFact, on_delete=models.CASCADE, related_name="evidence_links")
    evidence = models.ForeignKey(EvidenceAsset, on_delete=models.CASCADE, related_name="fact_links")
    notes = models.TextField(blank=True)
    linked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["fact", "evidence"], name="uniq_fact_evidence_link")
        ]

    def clean(self):
        if self.fact_id and self.evidence_id and self.fact.institution_id != self.evidence.institution_id:
            raise ValidationError("Fact and evidence must belong to the same institution.")


class MetricDataMapping(models.Model):
    class MappingType(models.TextChoices):
        DIRECT = "direct", "Direct value"
        AGGREGATE = "aggregate", "Aggregate"
        CALCULATED = "calculated", "Calculated / transformed"

    metric = models.ForeignKey(FrameworkMetric, on_delete=models.CASCADE, related_name="data_mappings")
    data_element = models.ForeignKey(DataElement, on_delete=models.PROTECT, related_name="metric_mappings")
    mapping_type = models.CharField(max_length=16, choices=MappingType.choices, default=MappingType.DIRECT)
    mapping_code = models.CharField(max_length=100, blank=True)
    transform_spec = models.JSONField(default=dict, blank=True, help_text="Declarative, reviewed mapping rule; do not execute arbitrary Python.")
    is_active = models.BooleanField(default=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_metric_mappings")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["metric", "data_element", "mapping_code"], name="uniq_metric_data_mapping")
        ]

    def __str__(self):
        return f"{self.metric} ← {self.data_element.key}"


class ReportSnapshot(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In review"
        FINALIZED = "finalized", "Finalized"
        EXPORTED = "exported", "Exported"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="report_snapshots")
    edition = models.ForeignKey(FrameworkEdition, on_delete=models.PROTECT, related_name="report_snapshots")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, null=True, blank=True, related_name="report_snapshots")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    payload = models.JSONField(default=dict, help_text="Frozen metric values, validations and evidence references for reproducibility.")
    checksum = models.CharField(max_length=64, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="generated_report_snapshots")
    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["institution", "edition", "status"])]

    def clean(self):
        if self.academic_year_id and self.institution_id and self.academic_year.institution_id != self.institution_id:
            raise ValidationError({"academic_year": "Academic year must belong to the same institution."})

    def __str__(self):
        return f"{self.institution.code} · {self.edition} · {self.title}"
