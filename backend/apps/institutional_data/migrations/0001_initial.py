# Generated for the multi-framework institutional data foundation.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Institution",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("institution_type", models.CharField(blank=True, max_length=80)),
                ("website", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Framework",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=160)),
                ("authority", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_enabled", models.BooleanField(default=True)),
                ("is_system", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="DataElement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(help_text="Stable key, e.g. faculty.full_time_count", max_length=160, unique=True)),
                ("label", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("value_type", models.CharField(choices=[("text", "Text"), ("integer", "Integer"), ("decimal", "Decimal"), ("boolean", "Boolean"), ("date", "Date"), ("record", "Structured record"), ("record_set", "Set of records")], default="text", max_length=16)),
                ("default_unit", models.CharField(blank=True, max_length=60)),
                ("scope_policy", models.JSONField(blank=True, default=dict, help_text="Allowed scopes and required context.")),
                ("validation_spec", models.JSONField(blank=True, default=dict)),
                ("sensitivity", models.CharField(default="internal", max_length=32)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["key"]},
        ),
        migrations.CreateModel(
            name="AcademicYear",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(help_text="Example: 2026-27", max_length=20)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("is_current", models.BooleanField(default=False)),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="academic_years", to="institutional_data.institution")),
            ],
            options={
                "ordering": ["-start_date"],
                "constraints": [
                    models.UniqueConstraint(fields=("institution", "label"), name="uniq_inst_academic_year"),
                    models.CheckConstraint(check=models.Q(end_date__gte=models.F("start_date")), name="academic_year_date_order"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50)),
                ("name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="departments", to="institutional_data.institution")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(fields=("institution", "code"), name="uniq_inst_department_code"),
                ],
            },
        ),
        migrations.CreateModel(
            name="InstitutionMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("institution_admin", "Institution administrator"), ("principal", "Principal / Director"), ("iqac_coordinator", "IQAC coordinator"), ("framework_coordinator", "Framework coordinator"), ("hod", "Head of department"), ("data_owner", "Data owner"), ("reviewer", "Reviewer"), ("auditor", "Auditor"), ("read_only", "Read-only")], max_length=32)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="institutional_data.institution")),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="institutional_data.department")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="institution_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("institution", "user", "role"), name="uniq_inst_user_role"),
                ],
                "indexes": [
                    models.Index(fields=["user", "is_active"], name="idmem_user_active_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Programme",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=60)),
                ("name", models.CharField(max_length=255)),
                ("award_level", models.CharField(blank=True, max_length=80)),
                ("duration_years", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="programmes", to="institutional_data.department")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [
                    models.UniqueConstraint(fields=("department", "code"), name="uniq_dept_programme_code"),
                ],
            },
        ),
        migrations.CreateModel(
            name="FrameworkEdition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.CharField(help_text="Authority edition / reporting cycle identifier", max_length=80)),
                ("title", models.CharField(blank=True, max_length=255)),
                ("effective_from", models.DateField(blank=True, null=True)),
                ("effective_to", models.DateField(blank=True, null=True)),
                ("applicability", models.JSONField(blank=True, default=dict, help_text="Reviewed rules for institution/programme categories.")),
                ("source_url", models.URLField(blank=True)),
                ("source_checked_at", models.DateTimeField(blank=True, null=True)),
                ("config_version", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("reviewed", "Reviewed"), ("active", "Active"), ("retired", "Retired")], default="draft", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("framework", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="editions", to="institutional_data.framework")),
            ],
            options={
                "ordering": ["framework__name", "-effective_from", "version"],
                "constraints": [
                    models.UniqueConstraint(fields=("framework", "version"), name="uniq_framework_edition_version"),
                ],
            },
        ),
        migrations.CreateModel(
            name="FrameworkCriterion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=80)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("guidance", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_applicable", models.BooleanField(default=True)),
                ("edition", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="criteria", to="institutional_data.frameworkedition")),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="institutional_data.frameworkcriterion")),
            ],
            options={
                "ordering": ["sort_order", "code"],
                "constraints": [
                    models.UniqueConstraint(fields=("edition", "code"), name="uniq_edition_criterion_code"),
                ],
            },
        ),
        migrations.CreateModel(
            name="FrameworkMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=100)),
                ("title", models.CharField(max_length=255)),
                ("definition", models.TextField(blank=True)),
                ("metric_type", models.CharField(choices=[("numeric", "Numeric"), ("text", "Text / narrative"), ("boolean", "Yes / no"), ("table", "Structured table"), ("evidence", "Evidence checklist"), ("obe", "Outcome-based education")], default="text", max_length=16)),
                ("unit", models.CharField(blank=True, max_length=60)),
                ("required", models.BooleanField(default=True)),
                ("formula_spec", models.JSONField(blank=True, default=dict, help_text="Version-controlled, reviewed calculation specification.")),
                ("validation_spec", models.JSONField(blank=True, default=dict)),
                ("output_spec", models.JSONField(blank=True, default=dict)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_applicable", models.BooleanField(default=True)),
                ("criterion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to="institutional_data.frameworkcriterion")),
            ],
            options={
                "ordering": ["sort_order", "code"],
                "constraints": [
                    models.UniqueConstraint(fields=("criterion", "code"), name="uniq_criterion_metric_code"),
                ],
            },
        ),
        migrations.CreateModel(
            name="InstitutionalFact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope_type", models.CharField(choices=[("institution", "Institution"), ("campus", "Campus"), ("department", "Department"), ("programme", "Programme"), ("cohort", "Student cohort"), ("person", "Person"), ("facility", "Facility"), ("activity", "Activity")], default="institution", max_length=20)),
                ("scope_key", models.CharField(blank=True, help_text="Stable scope identifier (e.g. department code or programme code).", max_length=160)),
                ("value", models.JSONField()),
                ("unit", models.CharField(blank=True, max_length=60)),
                ("source_system", models.CharField(blank=True, max_length=120)),
                ("source_record_id", models.CharField(blank=True, max_length=160)),
                ("definition_version", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted"), ("in_review", "In review"), ("approved", "Approved"), ("rejected", "Rejected"), ("superseded", "Superseded")], default="draft", max_length=16)),
                ("notes", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("academic_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="facts", to="institutional_data.academicyear")),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_institutional_facts", to=settings.AUTH_USER_MODEL)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_institutional_facts", to=settings.AUTH_USER_MODEL)),
                ("data_element", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="facts", to="institutional_data.dataelement")),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="facts", to="institutional_data.institution")),
                ("submitted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="submitted_institutional_facts", to=settings.AUTH_USER_MODEL)),
                ("supersedes", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="superseded_by", to="institutional_data.institutionalfact")),
                ("verified_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="verified_institutional_facts", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-updated_at"],
                "indexes": [
                    models.Index(fields=["institution", "academic_year", "status"], name="ifact_inst_year_status_idx"),
                    models.Index(fields=["data_element", "scope_type", "scope_key"], name="ifact_element_scope_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="EvidenceAsset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("storage_key", models.CharField(blank=True, help_text="Object-storage key; do not store file bytes in this column.", max_length=500)),
                ("external_url", models.URLField(blank=True)),
                ("source_system", models.CharField(blank=True, max_length=120)),
                ("source_record_id", models.CharField(blank=True, help_text="Optional identifier for an existing source document record.", max_length=160)),
                ("sha256", models.CharField(blank=True, max_length=64)),
                ("mime_type", models.CharField(blank=True, max_length=120)),
                ("file_size", models.PositiveBigIntegerField(blank=True, null=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("confidentiality", models.CharField(choices=[("public", "Public"), ("internal", "Internal"), ("confidential", "Confidential")], default="internal", max_length=16)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evidence_assets", to="institutional_data.institution")),
                ("supersedes", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="superseded_by", to="institutional_data.evidenceasset")),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="uploaded_evidence_assets", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-uploaded_at"],
                "indexes": [
                    models.Index(fields=["institution", "sha256"], name="evidence_inst_sha256_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="FactEvidenceLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notes", models.TextField(blank=True)),
                ("linked_at", models.DateTimeField(auto_now_add=True)),
                ("evidence", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fact_links", to="institutional_data.evidenceasset")),
                ("fact", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="evidence_links", to="institutional_data.institutionalfact")),
                ("linked_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("fact", "evidence"), name="uniq_fact_evidence_link"),
                ],
            },
        ),
        migrations.CreateModel(
            name="MetricDataMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mapping_type", models.CharField(choices=[("direct", "Direct value"), ("aggregate", "Aggregate"), ("calculated", "Calculated / transformed")], default="direct", max_length=16)),
                ("mapping_code", models.CharField(blank=True, max_length=100)),
                ("transform_spec", models.JSONField(blank=True, default=dict, help_text="Declarative, reviewed mapping rule; do not execute arbitrary Python.")),
                ("is_active", models.BooleanField(default=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("data_element", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="metric_mappings", to="institutional_data.dataelement")),
                ("metric", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_mappings", to="institutional_data.frameworkmetric")),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_metric_mappings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("metric", "data_element", "mapping_code"), name="uniq_metric_data_mapping"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ReportSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("in_review", "In review"), ("finalized", "Finalized"), ("exported", "Exported")], default="draft", max_length=16)),
                ("payload", models.JSONField(default=dict, help_text="Frozen metric values, validations and evidence references for reproducibility.")),
                ("checksum", models.CharField(blank=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finalized_at", models.DateTimeField(blank=True, null=True)),
                ("academic_year", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="report_snapshots", to="institutional_data.academicyear")),
                ("edition", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="report_snapshots", to="institutional_data.frameworkedition")),
                ("generated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="generated_report_snapshots", to=settings.AUTH_USER_MODEL)),
                ("institution", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="report_snapshots", to="institutional_data.institution")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["institution", "edition", "status"], name="report_inst_edition_idx"),
                ],
            },
        ),
    ]
