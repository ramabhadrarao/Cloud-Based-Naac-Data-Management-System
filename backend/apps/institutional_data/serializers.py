from rest_framework import serializers

from .models import (
    AcademicYear, DataElement, Department, EvidenceAsset, FactEvidenceLink, Framework,
    FrameworkCriterion, FrameworkEdition, FrameworkMetric, Institution,
    InstitutionalFact, MetricDataMapping, Programme, ReportSnapshot,
)


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ["id", "code", "name", "institution_type", "website", "is_active"]
        read_only_fields = fields


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "institution", "label", "start_date", "end_date", "is_current"]
        read_only_fields = fields


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "institution", "code", "name", "is_active"]
        read_only_fields = fields


class ProgrammeSerializer(serializers.ModelSerializer):
    institution_id = serializers.IntegerField(source="department.institution_id", read_only=True)

    class Meta:
        model = Programme
        fields = ["id", "institution_id", "department", "code", "name", "award_level", "duration_years", "is_active"]
        read_only_fields = fields


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = ["id", "code", "name", "authority", "description", "is_enabled"]


class FrameworkEditionSerializer(serializers.ModelSerializer):
    framework_code = serializers.CharField(source="framework.code", read_only=True)

    class Meta:
        model = FrameworkEdition
        fields = [
            "id", "framework", "framework_code", "version", "title",
            "effective_from", "effective_to", "applicability", "source_url",
            "source_checked_at", "config_version", "status",
        ]
        read_only_fields = fields


class FrameworkCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameworkCriterion
        fields = [
            "id", "edition", "parent", "code", "title", "description",
            "guidance", "sort_order", "is_applicable",
        ]
        read_only_fields = fields


class FrameworkMetricSerializer(serializers.ModelSerializer):
    criterion_code = serializers.CharField(source="criterion.code", read_only=True)
    framework_code = serializers.CharField(source="criterion.edition.framework.code", read_only=True)
    edition_version = serializers.CharField(source="criterion.edition.version", read_only=True)

    class Meta:
        model = FrameworkMetric
        fields = [
            "id", "criterion", "criterion_code", "framework_code", "edition_version",
            "code", "title", "definition", "metric_type", "unit", "required",
            "formula_spec", "validation_spec", "output_spec", "sort_order", "is_applicable",
        ]
        read_only_fields = fields


class DataElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataElement
        fields = [
            "id", "key", "label", "description", "value_type", "default_unit",
            "scope_policy", "validation_spec", "sensitivity", "is_active",
        ]
        read_only_fields = fields


class InstitutionalFactSerializer(serializers.ModelSerializer):
    data_element_key = serializers.CharField(source="data_element.key", read_only=True)
    academic_year_label = serializers.CharField(source="academic_year.label", read_only=True, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    submitted_by = serializers.PrimaryKeyRelatedField(read_only=True)
    verified_by = serializers.PrimaryKeyRelatedField(read_only=True)
    approved_by = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.ChoiceField(choices=InstitutionalFact.Status.choices, read_only=True)

    class Meta:
        model = InstitutionalFact
        fields = [
            "id", "institution", "academic_year", "academic_year_label",
            "data_element", "data_element_key", "scope_type", "scope_key",
            "value", "unit", "source_system", "source_record_id",
            "definition_version", "status", "notes", "submitted_by", "submitted_at",
            "verified_by", "verified_at", "approved_by", "approved_at",
            "supersedes", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "academic_year_label", "data_element_key", "status",
            "submitted_by", "submitted_at", "verified_by", "verified_at",
            "approved_by", "approved_at", "created_by", "created_at", "updated_at",
        ]

    @staticmethod
    def _matches_value_type(value, value_type):
        if value_type == "text":
            return isinstance(value, str)
        if value_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if value_type == "decimal":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if value_type == "boolean":
            return isinstance(value, bool)
        if value_type == "date":
            if not isinstance(value, str):
                return False
            from datetime import date
            try:
                date.fromisoformat(value)
                return True
            except ValueError:
                return False
        if value_type == "record":
            return isinstance(value, dict)
        if value_type == "record_set":
            return isinstance(value, list)
        return False

    def validate(self, attrs):
        request = self.context.get("request")
        institution = attrs.get("institution", getattr(self.instance, "institution", None))
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        supersedes = attrs.get("supersedes", getattr(self.instance, "supersedes", None))
        element = attrs.get("data_element", getattr(self.instance, "data_element", None))
        scope_type = attrs.get("scope_type", getattr(self.instance, "scope_type", "institution"))
        scope_key = attrs.get("scope_key", getattr(self.instance, "scope_key", ""))
        value = attrs.get("value", getattr(self.instance, "value", None))

        if self.instance and "institution" in attrs and attrs["institution"].id != self.instance.institution_id:
            raise serializers.ValidationError({"institution": "Institution is immutable. Create a new fact in the correct institution."})
        if element is not None:
            allowed_scopes = element.scope_policy.get("allowed_scopes", [])
            if allowed_scopes and scope_type not in allowed_scopes:
                raise serializers.ValidationError({"scope_type": "This scope is not allowed by the data-element definition."})
            if scope_type != "institution" and not scope_key:
                raise serializers.ValidationError({"scope_key": "A scope identifier is required for this scope type."})
            if element.scope_policy.get("academic_year_required") and academic_year is None:
                raise serializers.ValidationError({"academic_year": "This data element requires an academic year."})
            if ("value" in attrs or "data_element" in attrs) and not self._matches_value_type(value, element.value_type):
                raise serializers.ValidationError({"value": f"Value does not match the data element type '{element.value_type}'."})

        if self.instance and self.instance.status in (
            InstitutionalFact.Status.APPROVED, InstitutionalFact.Status.SUPERSEDED
        ):
            raise serializers.ValidationError(
                "Approved or superseded facts are immutable. Create a new fact and link it using 'supersedes'."
            )
        if institution and academic_year and academic_year.institution_id != institution.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to the selected institution."})
        if institution and supersedes and supersedes.institution_id != institution.id:
            raise serializers.ValidationError({"supersedes": "The prior fact must belong to the same institution."})
        if supersedes and element and (supersedes.data_element_id != element.id or supersedes.academic_year_id != getattr(academic_year, "id", None) or supersedes.scope_type != scope_type or supersedes.scope_key != scope_key):
            raise serializers.ValidationError({"supersedes": "A superseded fact must match the data element, academic year and scope."})

        if request and institution and not request.user.is_superuser:
            memberships = list(request.user.institution_memberships.filter(
                institution=institution, is_active=True, institution__is_active=True
            ).select_related("department"))
            if not memberships:
                raise serializers.ValidationError({"institution": "You do not have access to this institution."})
            from .permissions import GLOBAL_WRITE_ROLES, membership_can_scope_fact
            scope_allowed = any(
                (m.department_id is None and m.role != "hod")
                or (m.role in {"hod", "data_owner"} and membership_can_scope_fact(m, scope_type, scope_key))
                for m in memberships
            )
            if not scope_allowed:
                raise serializers.ValidationError({"scope_type": "Your membership cannot access this department/programme scope."})
        return attrs


class EvidenceAssetSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EvidenceAsset
        fields = [
            "id", "institution", "department", "title", "description", "storage_key", "external_url",
            "source_system", "source_record_id", "sha256", "mime_type", "file_size",
            "version", "confidentiality", "uploaded_by", "uploaded_at", "supersedes",
        ]
        read_only_fields = ["id", "uploaded_by", "uploaded_at", "version"]

    def validate(self, attrs):
        request = self.context.get("request")
        institution = attrs.get("institution", getattr(self.instance, "institution", None))
        supersedes = attrs.get("supersedes", getattr(self.instance, "supersedes", None))
        storage_key = attrs.get("storage_key", getattr(self.instance, "storage_key", ""))
        external_url = attrs.get("external_url", getattr(self.instance, "external_url", ""))
        source_record_id = attrs.get("source_record_id", getattr(self.instance, "source_record_id", ""))
        if not (storage_key or external_url or source_record_id):
            raise serializers.ValidationError("Provide a storage key, external URL, or source record reference.")
        if self.instance and "institution" in attrs and attrs["institution"].id != self.instance.institution_id:
            raise serializers.ValidationError({"institution": "Institution is immutable. Create a new evidence record in the correct institution."})
        department = attrs.get("department", getattr(self.instance, "department", None))
        if self.instance and "department" in attrs and getattr(attrs["department"], "id", None) != self.instance.department_id:
            raise serializers.ValidationError({"department": "Evidence department is immutable; create a new version in the correct scope."})
        if department and institution and department.institution_id != institution.id:
            raise serializers.ValidationError({"department": "Department must belong to the selected institution."})
        if institution and supersedes and supersedes.institution_id != institution.id:
            raise serializers.ValidationError({"supersedes": "Prior evidence must belong to the same institution."})
        if department and supersedes and supersedes.department_id != department.id:
            raise serializers.ValidationError({"supersedes": "Superseded evidence must belong to the same department scope."})
        if request and institution and not request.user.is_superuser:
            allowed = request.user.institution_memberships.filter(
                institution=institution, is_active=True
            ).exists()
            if not allowed:
                raise serializers.ValidationError({"institution": "You do not have access to this institution."})
        return attrs


class FactEvidenceLinkSerializer(serializers.ModelSerializer):
    linked_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FactEvidenceLink
        fields = ["id", "fact", "evidence", "notes", "linked_by", "linked_at"]
        read_only_fields = ["id", "linked_by", "linked_at"]

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields["fact"].read_only = True
            fields["evidence"].read_only = True
        return fields

    def validate(self, attrs):
        fact = attrs.get("fact", getattr(self.instance, "fact", None))
        evidence = attrs.get("evidence", getattr(self.instance, "evidence", None))
        if fact and evidence and fact.institution_id != evidence.institution_id:
            raise serializers.ValidationError("Fact and evidence must belong to the same institution.")
        if fact and evidence and evidence.department_id:
            department = evidence.department
            matches_department = fact.scope_type == InstitutionalFact.ScopeType.DEPARTMENT and fact.scope_key == department.code
            from .models import Programme
            matches_programme = fact.scope_type == InstitutionalFact.ScopeType.PROGRAMME and Programme.objects.filter(department=department, code=fact.scope_key).exists()
            if not (matches_department or matches_programme):
                raise serializers.ValidationError("Department-scoped evidence must support a fact in that department or its programme.")
        return attrs


class MetricDataMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricDataMapping
        fields = [
            "id", "metric", "data_element", "mapping_type", "mapping_code",
            "transform_spec", "is_active", "reviewed_by", "reviewed_at",
        ]
        read_only_fields = fields


class ReportSnapshotSerializer(serializers.ModelSerializer):
    framework_code = serializers.CharField(source="edition.framework.code", read_only=True)
    edition_version = serializers.CharField(source="edition.version", read_only=True)

    class Meta:
        model = ReportSnapshot
        fields = [
            "id", "institution", "edition", "framework_code", "edition_version",
            "academic_year", "title", "status", "payload", "checksum",
            "generated_by", "created_at", "finalized_at",
        ]
        read_only_fields = fields
