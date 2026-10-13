from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import InstitutionMembership, Programme


GLOBAL_READ_ROLES = {
    InstitutionMembership.Role.INSTITUTION_ADMIN,
    InstitutionMembership.Role.PRINCIPAL,
    InstitutionMembership.Role.IQAC_COORDINATOR,
    InstitutionMembership.Role.FRAMEWORK_COORDINATOR,
    InstitutionMembership.Role.REVIEWER,
    InstitutionMembership.Role.AUDITOR,
    InstitutionMembership.Role.READ_ONLY,
}
GLOBAL_WRITE_ROLES = {
    InstitutionMembership.Role.INSTITUTION_ADMIN,
    InstitutionMembership.Role.PRINCIPAL,
    InstitutionMembership.Role.IQAC_COORDINATOR,
    InstitutionMembership.Role.FRAMEWORK_COORDINATOR,
}
WRITE_ROLES = GLOBAL_WRITE_ROLES | {
    InstitutionMembership.Role.HOD,
    InstitutionMembership.Role.DATA_OWNER,
}


def _institution_id_for_object(obj):
    direct_id = getattr(obj, "institution_id", None)
    if direct_id:
        return direct_id
    department = getattr(obj, "department", None)
    if department is not None:
        return getattr(department, "institution_id", None)
    fact = getattr(obj, "fact", None)
    if fact is not None:
        return getattr(fact, "institution_id", None)
    return None


def is_global_membership(membership):
    if membership.department_id:
        return False
    if membership.role == InstitutionMembership.Role.HOD:
        return False
    return membership.role in GLOBAL_READ_ROLES or membership.role == InstitutionMembership.Role.DATA_OWNER


def membership_can_scope_fact(membership, scope_type, scope_key):
    """Return whether a department-bound member may use the supplied fact scope."""
    department = membership.department
    if department is None:
        return is_global_membership(membership)
    if scope_type == "department":
        return scope_key == department.code
    if scope_type == "programme":
        return Programme.objects.filter(department=department, code=scope_key).exists()
    return False


def membership_can_access_object(membership, obj):
    """Department-bound HOD/data owners only see objects scoped to their department."""
    if is_global_membership(membership):
        return True
    department = membership.department
    if department is None or membership.role not in {InstitutionMembership.Role.HOD, InstitutionMembership.Role.DATA_OWNER}:
        return False

    model_name = obj._meta.model_name
    if model_name == "department":
        return obj.pk == department.pk
    if model_name == "programme":
        return obj.department_id == department.pk
    if model_name == "academicyear":
        return True
    if model_name == "institution":
        return True
    if model_name == "institutionalfact":
        return membership_can_scope_fact(membership, obj.scope_type, obj.scope_key)
    if model_name == "evidenceasset":
        return obj.department_id == department.pk
    if model_name == "factevidencelink":
        fact_ok = membership_can_scope_fact(membership, obj.fact.scope_type, obj.fact.scope_key)
        evidence_ok = obj.evidence.department_id == department.pk
        return fact_ok and evidence_ok
    # Institution-wide report snapshots are not visible to department-only roles.
    if model_name == "reportsnapshot":
        return False
    return False


def membership_can_write_object(membership, obj):
    if membership.role in GLOBAL_WRITE_ROLES and membership.department_id is None:
        return True
    if membership.role == InstitutionMembership.Role.DATA_OWNER and membership.department_id is None:
        return True
    if membership.role not in {InstitutionMembership.Role.HOD, InstitutionMembership.Role.DATA_OWNER}:
        return False
    return membership_can_access_object(membership, obj)


class HasInstitutionalAccess(BasePermission):
    """Require an active institutional membership and enforce its institution/department scope."""

    message = "Active membership and the required role/scope for this institution are needed."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        memberships = InstitutionMembership.objects.filter(
            user=user, is_active=True, institution__is_active=True
        )
        if not memberships.exists():
            return False
        if request.method in SAFE_METHODS:
            return True
        return memberships.filter(role__in=WRITE_ROLES).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        institution_id = _institution_id_for_object(obj)
        if institution_id is None:
            return request.method in SAFE_METHODS
        memberships = InstitutionMembership.objects.filter(
            user=user,
            institution_id=institution_id,
            is_active=True,
            institution__is_active=True,
        ).select_related("department")
        for membership in memberships:
            if request.method in SAFE_METHODS and membership_can_access_object(membership, obj):
                return True
            if request.method not in SAFE_METHODS and membership_can_write_object(membership, obj):
                return True
        return False
