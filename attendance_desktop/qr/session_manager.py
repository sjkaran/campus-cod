"""QR session adapter.

NOTE: The original deskapk/ QR code could not be inspected when this node was built.
This module is the ONE place where deskapk's session/token/duplicate logic should be
dropped in. Keep the public interface (token, mark, remaining, close) unchanged.
Client-side checks are NOT authoritative; the backend re-validates in Stage 2.
"""
import hashlib, secrets, time
from datetime import datetime
from models.models import AttendanceRecord

class QrError(Exception): ...
class InvalidQr(QrError): ...
class ExpiredSession(QrError): ...
class SessionClosed(QrError): ...
class DuplicateScan(QrError): ...

class QrSessionManager:
    def __init__(self, session_id: str, duration_s: int, rotate_s: int):
        self.session_id, self.rotate_s = session_id, rotate_s
        self._secret, self._t0 = secrets.token_hex(8), time.time()
        self.ends_at, self.open = self._t0 + duration_s, True
        self.records: dict[str, AttendanceRecord] = {}
        self.rejected: list[tuple[str, str]] = []

    def _epoch(self) -> int: return int((time.time() - self._t0) // self.rotate_s)
    def _sig(self, e: int) -> str:
        return hashlib.sha256(f"{self.session_id}{e}{self._secret}".encode()).hexdigest()[:10]

    def token(self) -> str:
        e = self._epoch(); return f"SC|{self.session_id}|{e}|{self._sig(e)}"

    def remaining(self) -> int: return max(0, int(self.ends_at - time.time())) if self.open else 0
    def accepting(self) -> bool: return self.open and self.remaining() > 0
    def close(self) -> None: self.open = False

    def mark(self, student_id: str, token: str) -> AttendanceRecord:
        try:
            if not self.open: raise SessionClosed("This session is closed.")
            if self.remaining() <= 0: raise ExpiredSession("QR session expired.")
            parts = token.split("|")
            if len(parts) != 4 or parts[0] != "SC" or parts[1] != self.session_id: raise InvalidQr("Invalid QR code.")
            e = int(parts[2])
            if parts[3] != self._sig(e) or e < self._epoch() - 1: raise InvalidQr("QR code is invalid or outdated.")
            if student_id in self.records: raise DuplicateScan("Attendance already recorded for this session.")
        except (QrError, ValueError) as ex:
            err = ex if isinstance(ex, QrError) else InvalidQr("Invalid QR code.")
            self.rejected.append((student_id, str(err))); raise err
        rec = AttendanceRecord(student_id, self.session_id, "PRESENT", datetime.now().strftime("%H:%M:%S"))
        self.records[student_id] = rec
        return rec
