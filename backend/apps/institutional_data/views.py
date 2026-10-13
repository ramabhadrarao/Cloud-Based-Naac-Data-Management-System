from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    AcademicYear, DataElement, Department, EvidenceAsset, Framework,
    FrameworkCriterion, FrameworkEdition, FrameworkMetric, Institution,
    InstitutionMembership, InstitutionalFact, MetricDataMapping, Programme,
    ReportSnapshot,
)
from .permissions import HasInstitutionalAccess, WRITE_ROLES
from .serializers import (
    AcademicYearSerializer, DataElementSerializer, DepartmentSerializer,
    EvidenceAssetSerializer, FrameworkCriterionSerializer, FrameworkEditionSerializer,
    FrameworkMetricSerializer, FrameworkSerializer, InstitutionSerializer,
    InstitutionalFactSerializer, MetricDataMappingSerializer, ProgrammeSerializer,
    ReportSnapshotSerializer,
)


class InstitutionScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]
    institution_path = "institution_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        institution_ids = InstitutionMembership.objects.filter(
            user=user, is_active=True, institution__is_active=True
        ).values_list("institution_id", flat=True)
        return queryset.filter(**{f"{self.institution_path}__in": institution_ids})

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            serializer.save(**self.create_user_fields())
            return
        institution = serializer.validated_data.get("institution")
        if institution is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"institution": "An institution must be provided."})
        role_allowed = InstitutionMembership.objects.filter(
            user=user, institution=institution, is_active=True, institution__is_active=True,
            role__in=WRITE_ROLES,
        ).exists()
        if not role_allowed:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Your role cannot create records for this institution.")
        serializer.save(**self.create_user_fields())

    def create_user_fields(self):
        return {}


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
        ids = InstitutionMembership.objects.filter(user=self.request.user, is_active=True).values_list("institution_id", flat=True)
        return qs.filter(institution_id__in=ids)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.select_related("institution").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        ids = InstitutionMembership.objects.filter(user=self.request.user, is_active=True).values_list("institution_id", flat=True)
        return qs.filter(institution_id__in=ids)


class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.select_related("department", "department__institution").all()
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAuthenticated, HasInstitutionalAccess]
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        ids = InstitutionMembership.objects.filter(user=self.request.user, is_active=True).values_list("institution_id", flat=True)
        return qs.filter(department__institution_id__in=ids)


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
        super().perform_create(serializer)

    def create_user_fields(self):
        return {"created_by": self.request.user}


class EvidenceAssetViewSet(InstitutionScopedViewSet):
    queryset = EvidenceAsset.objects.select_related("institution", "uploaded_by").all()
    serializer_class = EvidenceAssetSerializer
    institution_path = "institution_id"

    def create_user_fields(self):
        return {"uploaded_by": self.request.user}


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
        ids = InstitutionMembership.objects.filter(user=self.request.user, is_active=True).values_list("institution_id", flat=True)
        return qs.filter(institution_id__in=ids)
