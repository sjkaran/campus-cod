"""Data model for the authenticated Admin user."""

from dataclasses import dataclass


@dataclass
class Admin:
    admin_id: str
    username: str
    name: str
    designation: str
    department: str
    email: str

    @property
    def initials(self) -> str:
        parts = self.name.split()
        return "".join(p[0].upper() for p in parts[:2]) if parts else "A"
