from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import InstitutionMembership


WRITE_ROLES = {
    InstitutionMembership.Role.INSTITUTION_ADMIN,
    InstitutionMembership.Role.PRINCIPAL,
    InstitutionMembership.Role.IQAC_COORDINATOR,
    InstitutionMembership.Role.FRAMEWORK_COORDINATOR,
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


class HasInstitutionalAccess(BasePermission):
    """Require an active institutional membership; enforce write roles for scoped data."""

    message = "Active membership and the required role for this institution are needed."
    allowed_write_roles = WRITE_ROLES

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        memberships = InstitutionMembership.objects.filter(user=user, is_active=True, institution__is_active=True)
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
        membership = InstitutionMembership.objects.filter(
            user=user, institution_id=institution_id, is_active=True, institution__is_active=True
        ).first()
        if not membership:
            return False
        return request.method in SAFE_METHODS or membership.role in WRITE_ROLES
