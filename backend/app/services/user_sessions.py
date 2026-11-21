"""Start, find and end the sessions that keep users signed in."""

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, joinedload

from app.config import SESSION_MINUTES
from app.models import User, UserSession


def start_session(db: Session, user: User, now: datetime) -> UserSession:
    _delete_expired_sessions(db, user, now)
    session = UserSession(
        id=str(uuid4()), user=user, expires_at=now + timedelta(minutes=SESSION_MINUTES)
    )
    db.add(session)
    db.commit()
    return session


def find_active_session(db: Session, session_id: str, now: datetime) -> UserSession | None:
    statement = (
        select(UserSession)
        .options(joinedload(UserSession.user))
        .where(UserSession.id == session_id)
    )
    session = db.scalar(statement)
    return session if session is not None and session.is_active(now) else None


def end_session(db: Session, session: UserSession, now: datetime) -> None:
    session.ended_at = now
    db.commit()


def end_other_sessions(db: Session, kept: UserSession, now: datetime) -> None:
    db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == kept.user_id,
            UserSession.id != kept.id,
            UserSession.ended_at.is_(None),
        )
        .values(ended_at=now)
    )
    db.commit()


def _delete_expired_sessions(db: Session, user: User, now: datetime) -> None:
    db.execute(
        delete(UserSession).where(UserSession.user_id == user.id, UserSession.expires_at <= now)
    )
