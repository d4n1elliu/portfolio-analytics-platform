"""Slow down password guessing by limiting failed sign-ins. Uses no database.

Failures are kept in memory, so the count starts again when the app restarts
and is not shared between copies of the app.
"""

from collections import deque
from datetime import datetime, timedelta
from threading import Lock

MAX_FAILURES = 10
WINDOW = timedelta(minutes=15)


class LoginLimiter:
    """Counts the recent failed sign-ins from each address."""

    def __init__(self, max_failures: int = MAX_FAILURES, window: timedelta = WINDOW):
        self.max_failures = max_failures
        self.window = window
        self._failures: dict[str, deque[datetime]] = {}
        # Requests are handled on several threads at once.
        self._lock = Lock()

    def record_failure(self, address: str, now: datetime) -> None:
        with self._lock:
            self._forget_old_failures(now)
            self._failures.setdefault(address, deque()).append(now)

    def retry_after(self, address: str, now: datetime) -> timedelta | None:
        """Return how long the address must wait, or None if it may try now."""
        with self._lock:
            self._forget_old_failures(now)
            failures = self._failures.get(address, ())
            if len(failures) < self.max_failures:
                return None
            # The address may try again once its oldest failure is outside the window.
            return failures[0] + self.window - now

    def _forget_old_failures(self, now: datetime) -> None:
        """Drop failures older than the window, so the memory used stays small."""
        earliest = now - self.window
        for address in list(self._failures):
            failures = self._failures[address]
            while failures and failures[0] <= earliest:
                failures.popleft()
            if not failures:
                del self._failures[address]
