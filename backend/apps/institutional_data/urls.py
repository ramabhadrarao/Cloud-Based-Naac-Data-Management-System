from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet, DataElementViewSet, DepartmentViewSet, EvidenceAssetViewSet,
    FrameworkCriterionViewSet, FrameworkEditionViewSet, FrameworkMetricViewSet,
    FrameworkViewSet, InstitutionViewSet, InstitutionalFactViewSet,
    MetricDataMappingViewSet, ProgrammeViewSet, ReportSnapshotViewSet,
)

router = DefaultRouter()
router.register("institutions", InstitutionViewSet, basename="institution")
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("departments", DepartmentViewSet, basename="department")
router.register("programmes", ProgrammeViewSet, basename="programme")
router.register("frameworks", FrameworkViewSet, basename="framework")
router.register("framework-editions", FrameworkEditionViewSet, basename="framework-edition")
router.register("criteria", FrameworkCriterionViewSet, basename="framework-criterion")
router.register("metrics", FrameworkMetricViewSet, basename="framework-metric")
router.register("data-elements", DataElementViewSet, basename="data-element")
router.register("facts", InstitutionalFactViewSet, basename="institutional-fact")
router.register("evidence", EvidenceAssetViewSet, basename="evidence-asset")
router.register("metric-mappings", MetricDataMappingViewSet, basename="metric-data-mapping")
router.register("report-snapshots", ReportSnapshotViewSet, basename="report-snapshot")

urlpatterns = router.urls
