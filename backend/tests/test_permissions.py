"""What each role is allowed to do. No database is used."""

from app.models import Role
from app.services.permissions import ROLE_PERMISSIONS, Permission, permissions_of


def test_every_role_has_its_permissions_listed():
    assert set(ROLE_PERMISSIONS) == set(Role)


def test_each_role_can_do_more_than_the_one_below_it():
    analyst = permissions_of(Role.ANALYST)
    portfolio_manager = permissions_of(Role.PORTFOLIO_MANAGER)
    operations = permissions_of(Role.OPERATIONS)

    assert analyst == set()
    assert portfolio_manager == {Permission.EXPORT_TRADES}
    assert operations == {Permission.EXPORT_TRADES, Permission.IMPORT_TRADES}
    assert analyst < portfolio_manager < operations
