"""Database models.

Every model is imported here, so "import app.models" registers all the tables
on Base.metadata, which is what Alembic reads. When you add a model file,
import it here too.

Other code can then import everything from one place:
    from app.models import Security, Trade, TradeSide
"""

from app.models.price import Price
from app.models.security import Security
from app.models.trade import Trade, TradeSide
from app.models.user import Role, User

__all__ = ["Price", "Role", "Security", "Trade", "TradeSide", "User"]
