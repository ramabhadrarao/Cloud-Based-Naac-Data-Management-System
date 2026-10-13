from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import (
    AcademicYear, DataElement, Department, EvidenceAsset, FactEvidenceLink, Framework,
    FrameworkCriterion, FrameworkEdition, FrameworkMetric, Institution,
    InstitutionMembership, InstitutionalFact, MetricDataMapping, Programme,
    ReportSnapshot,
)
from .permissions import (
    GLOBAL_WRITE_ROLES, WRITE_ROLES, HasInstitutionalAccess,
    is_global_membership, membership_can_access_object, membership_can_scope_fact,
    membership_can_write_object,
)
from .serializers import (
    AcademicYearSerializer, DataElementSerializer, DepartmentSerializer,
    EvidenceAssetSerializer, FactEvidenceLinkSerializer, FrameworkCriterionSerializer,
    FrameworkEditionSerializer, FrameworkMetricSerializer, FrameworkSerializer,
    InstitutionSerializer, InstitutionalFactSerializer, MetricDataMappingSerializer,
    ProgrammeSerializer, ReportSnapshotSerializer,
)


DEPARTMENT_SCOPED_ROLES = {
    InstitutionMembership.Role.HOD,
    InstitutionMembership.Role.DATA_OWNER,
}


def _memberships_for(user):
    return list(
        InstitutionMembership.objects.filter(
            user=user, is_active=True, institution__is_active=True
        ).select_related("institution", "department")
    )


def _global_institution_ids(memberships):
    return {m.institution_id for m in memberships if is_global_membership(m)}


def _department_memberships(memberships):
    return [m for m in memberships if m.department_id and m.role in DEPARTMENT_SCOPED_ROLES]


def _scoped_fact_query(memberships, prefix=""):
    query = Q(pk__in=[])
    for membership in _department_memberships(memberships):
        field = f"{prefix}scope_type"
        key_field = f"{prefix}scope_key"
        institution_field = f"{prefix}institution_id"
        query |= Q(**{
            institution_field: membership.institution_id,
            field: InstitutionalFact.ScopeType.DEPARTMENT,
            key_field: membership.department.code,
        })
        programme_codes = Programme.objects.filter(
            department_id=membership.department_id
        ).values_list("code", flat=True)
        query |= Q(**{
            institution_field: membership.institution_id,
            field: InstitutionalFact.ScopeType.PROGRAMME,
            f"{key_field}__in": programme_codes,
        })
    return query


def _filter_institution_scoped_queryset(queryset, user, institution_path="institution_id"):
    memberships = _memberships_for(user)
    global_ids = _global_institution_ids(memberships)
    scoped = _department_memberships(memberships)
    model_name = queryset.model._meta.model_name

    if model_name == "institutionalfact":
        query = Q(institution_id__in=global_ids) | _scoped_fact_query(scoped)
        return queryset.filter(query).distinct()

    if model_name == "evidenceasset":
        query = Q(institution_id__in=global_ids)
        for membership in scoped:
            query |= Q(institution_id=membership.institution_id, department_id=membership.department_id)
        return queryset.filter(query).distinct()

    if model_name == "factevidencelink":
        query = Q(fact__institution_id__in=global_ids)
        for membership in scoped:
            fact_query = _scoped_fact_query([membership], prefix="fact__")
            query |= Q(fact_query, evidence__department_id=membership.department_id)
        return queryset.filter(query).distinct()

    return queryset.filter(**{f"{institution_path}__in": [m.institution_id for m in memberships]})


def _membership_can_create_fact(membership, institution, scope_type, scope_key):
    if membership.institution_id != institution.id or not membership.is_active:
        return False
    if membership.role in GLOBAL_WRITE_ROLES and membership.department_id is None:
        return True
    if membership.role == InstitutionMembership.Role.DATA_OWNER and membership.department_id is None:
        return True
    return (
        membership.role in DEPARTMENT_SCOPED_ROLES
        and membership_can_scope_fact(membership, scope_type, scope_key)
    )


class InstitutionScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]
    institution_path = "institution_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return _filter_institution_scoped_queryset(
            queryset, self.request.user, institution_path=self.institution_path
        )


class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        ids = InstitutionMembership.objects.filter(
            user=self.request.user, is_active=True, institution__is_active=True
        ).values_list("institution_id", flat=True)
        return queryset.filter(id__in=ids)


class AcademicYearViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AcademicYear.objects.select_related("institution").all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        ids = InstitutionMembership.objects.filter(
            user=self.request.user, is_active=True, institution__is_active=True
        ).values_list("institution_id", flat=True)
        return qs.filter(institution_id__in=ids)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.select_related("institution").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        memberships = _memberships_for(self.request.user)
        global_ids = _global_institution_ids(memberships)
        department_ids = [m.department_id for m in _department_memberships(memberships)]
        return qs.filter(Q(institution_id__in=global_ids) | Q(id__in=department_ids)).distinct()


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.select_related("department", "department__institution").all()
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        memberships = _memberships_for(self.request.user)
        global_ids = _global_institution_ids(memberships)
        department_ids = [m.department_id for m in _department_memberships(memberships)]
        return qs.filter(
            Q(department__institution_id__in=global_ids) | Q(department_id__in=department_ids)
        ).distinct()


class FrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Framework.objects.filter(is_enabled=True)
    serializer_class = FrameworkSerializer
    permission_classes = [IsAuthenticated]


class FrameworkEditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FrameworkEdition.objects.select_related("framework").all()
    serializer_class = FrameworkEditionSerializer
    permission_classes = [IsAuthenticated]


class FrameworkCriterionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FrameworkCriterion.objects.select_related("edition", "edition__framework").all()
    serializer_class = FrameworkCriterionSerializer
    permission_classes = [IsAuthenticated]


class FrameworkMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FrameworkMetric.objects.select_related("criterion", "criterion__edition", "criterion__edition__framework").all()
    serializer_class = FrameworkMetricSerializer
    permission_classes = [IsAuthenticated]


class DataElementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DataElement.objects.filter(is_active=True)
    serializer_class = DataElementSerializer
    permission_classes = [IsAuthenticated]


class InstitutionalFactViewSet(InstitutionScopedViewSet):
    queryset = InstitutionalFact.objects.select_related("institution", "academic_year", "data_element").all()
    serializer_class = InstitutionalFactSerializer
    institution_path = "institution_id"

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save(created_by=user)
            return
        institution = serializer.validated_data["institution"]
        scope_type = serializer.validated_data.get("scope_type", InstitutionalFact.ScopeType.INSTITUTION)
        scope_key = serializer.validated_data.get("scope_key", "")
        if not any(
            _membership_can_create_fact(m, institution, scope_type, scope_key)
            for m in _memberships_for(user)
        ):
            raise PermissionDenied("Your role and department scope do not allow this fact to be created.")
        serializer.save(created_by=user)


class EvidenceAssetViewSet(InstitutionScopedViewSet):
    queryset = EvidenceAsset.objects.select_related("institution", "department", "uploaded_by").all()
    serializer_class = EvidenceAssetSerializer
    institution_path = "institution_id"

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save(uploaded_by=user)
            return
        institution = serializer.validated_data["institution"]
        department = serializer.validated_data.get("department")
        memberships = [m for m in _memberships_for(user) if m.institution_id == institution.id]
        for membership in memberships:
            if membership.role in GLOBAL_WRITE_ROLES and membership.department_id is None:
                serializer.save(uploaded_by=user)
                return
            if membership.role == InstitutionMembership.Role.DATA_OWNER and membership.department_id is None:
                serializer.save(uploaded_by=user)
                return
            if membership.role in DEPARTMENT_SCOPED_ROLES and membership.department_id:
                if department is not None and department.id != membership.department_id:
                    continue
                serializer.save(uploaded_by=user, department=membership.department)
                return
        raise PermissionDenied("Your role and department scope do not allow this evidence to be created.")


class FactEvidenceLinkViewSet(InstitutionScopedViewSet):
    queryset = FactEvidenceLink.objects.select_related(
        "fact", "fact__institution", "fact__data_element",
        "evidence", "evidence__department", "linked_by",
    ).all()
    serializer_class = FactEvidenceLinkSerializer
    institution_path = "fact__institution_id"

    def perform_create(self, serializer):
        user = self.request.user
        fact = serializer.validated_data["fact"]
        evidence = serializer.validated_data["evidence"]
        if fact.institution_id != evidence.institution_id:
            raise ValidationError("Fact and evidence must belong to the same institution.")
        if evidence.department_id:
            department = evidence.department
            matches_department = fact.scope_type == InstitutionalFact.ScopeType.DEPARTMENT and fact.scope_key == department.code
            matches_programme = (
                fact.scope_type == InstitutionalFact.ScopeType.PROGRAMME
                and Programme.objects.filter(department=department, code=fact.scope_key).exists()
            )
            if not (matches_department or matches_programme):
                raise ValidationError("Department-scoped evidence must support a fact scoped to that department or programme.")
        if user.is_superuser:
            serializer.save(linked_by=user)
            return
        memberships = InstitutionMembership.objects.filter(
            user=user, institution_id=fact.institution_id, is_active=True, institution__is_active=True
        ).select_related("department")
        if not any(
            membership_can_write_object(m, fact) and membership_can_write_object(m, evidence)
            for m in memberships
        ):
            raise PermissionDenied("Your role and department scope do not allow this evidence link.")
        serializer.save(linked_by=user)


class MetricDataMappingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetricDataMapping.objects.select_related("metric", "metric__criterion", "data_element").filter(is_active=True)
    serializer_class = MetricDataMappingSerializer
    permission_classes = [IsAuthenticated]


class ReportSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportSnapshot.objects.select_related("institution", "edition", "edition__framework", "academic_year").all()
    serializer_class = ReportSnapshotSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        memberships = _memberships_for(self.request.user)
        global_ids = _global_institution_ids(memberships)
        return qs.filter(institution_id__in=global_ids)
