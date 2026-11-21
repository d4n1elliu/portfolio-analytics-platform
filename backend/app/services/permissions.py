"""What each role is allowed to do, beyond viewing. Uses no database."""

from enum import StrEnum

from app.models import Role


class Permission(StrEnum):
    IMPORT_TRADES = "import_trades"
    EXPORT_TRADES = "export_trades"
    UPLOAD_RESEARCH = "upload_research"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OPERATIONS: frozenset(
        {Permission.IMPORT_TRADES, Permission.EXPORT_TRADES, Permission.UPLOAD_RESEARCH}
    ),
    Role.PORTFOLIO_MANAGER: frozenset({Permission.EXPORT_TRADES}),
    Role.ANALYST: frozenset({Permission.UPLOAD_RESEARCH}),
}


def permissions_of(role: str) -> frozenset[Permission]:
    return ROLE_PERMISSIONS[Role(role)]
