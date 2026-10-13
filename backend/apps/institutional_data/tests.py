from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.institutional_data.models import (
    AcademicYear, DataElement, EvidenceAsset, FactEvidenceLink, Framework,
    FrameworkCriterion, FrameworkEdition, FrameworkMetric, Institution,
    InstitutionMembership, InstitutionalFact, MetricDataMapping,
)


class InstitutionalDataModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="iqac-test", password="test-only-password")
        self.institution = Institution.objects.create(code="demo-college", name="Demo Autonomous College")
        self.year = AcademicYear.objects.create(
            institution=self.institution,
            label="2026-27",
            start_date=date(2026, 6, 1),
            end_date=date(2027, 5, 31),
        )
        self.element = DataElement.objects.create(
            key="faculty.full_time_count",
            label="Full-time faculty count",
            value_type=DataElement.ValueType.INTEGER,
            default_unit="persons",
        )

    def test_membership_unique_per_institution_and_user(self):
        InstitutionMembership.objects.create(
            institution=self.institution, user=self.user,
            role=InstitutionMembership.Role.IQAC_COORDINATOR,
        )
        with self.assertRaises(Exception):
            InstitutionMembership.objects.create(
                institution=self.institution, user=self.user,
                role=InstitutionMembership.Role.DATA_OWNER,
            )

    def test_fact_must_use_academic_year_from_same_institution(self):
        other = Institution.objects.create(code="other-college", name="Other College")
        other_year = AcademicYear.objects.create(
            institution=other, label="2026-27",
            start_date=date(2026, 6, 1), end_date=date(2027, 5, 31),
        )
        fact = InstitutionalFact(
            institution=self.institution, academic_year=other_year,
            data_element=self.element, value=84, created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            fact.full_clean()

    def test_approved_fact_requires_approver(self):
        fact = InstitutionalFact(
            institution=self.institution, academic_year=self.year,
            data_element=self.element, value=84,
            status=InstitutionalFact.Status.APPROVED, created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            fact.full_clean()

    def test_fact_and_evidence_must_belong_to_same_institution(self):
        other = Institution.objects.create(code="other-college", name="Other College")
        fact = InstitutionalFact.objects.create(
            institution=self.institution, academic_year=self.year,
            data_element=self.element, value=84, created_by=self.user,
        )
        evidence = EvidenceAsset(
            institution=other, title="Supporting statement",
            external_url="https://example.org/evidence.pdf", uploaded_by=self.user,
        )
        evidence.save()
        link = FactEvidenceLink(fact=fact, evidence=evidence, linked_by=self.user)
        with self.assertRaises(ValidationError):
            link.full_clean()

    def test_metric_mapping_is_framework_specific_but_data_element_is_shared(self):
        framework = Framework.objects.create(code="nirf-test", name="NIRF test")
        edition = FrameworkEdition.objects.create(framework=framework, version="test-edition")
        criterion = FrameworkCriterion.objects.create(edition=edition, code="TLR", title="Teaching, learning and resources")
        metric = FrameworkMetric.objects.create(criterion=criterion, code="faculty", title="Faculty metric")
        mapping = MetricDataMapping.objects.create(metric=metric, data_element=self.element)
        self.assertEqual(mapping.data_element.key, "faculty.full_time_count")
        self.assertEqual(mapping.metric.criterion.edition.framework.code, "nirf-test")
