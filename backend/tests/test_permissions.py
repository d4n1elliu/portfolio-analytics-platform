"""What each role is allowed to do. No database is used."""

from app.models import Role
from app.services.permissions import ROLE_PERMISSIONS, Permission, permissions_of


def test_every_role_has_its_permissions_listed():
    assert set(ROLE_PERMISSIONS) == set(Role)


def test_each_role_has_its_own_permissions():
    assert permissions_of(Role.ANALYST) == {Permission.UPLOAD_RESEARCH}
    assert permissions_of(Role.PORTFOLIO_MANAGER) == {Permission.EXPORT_TRADES}
    assert permissions_of(Role.OPERATIONS) == set(Permission)
