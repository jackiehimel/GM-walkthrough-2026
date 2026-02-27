# app/models.py — SQLModel domain models
from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# -----------------------------------------------------------------------------
# Enums (used in forms, filters, and DB)
# -----------------------------------------------------------------------------
class GuestTier(str, Enum):
    platinum = "platinum"
    gold = "gold"
    silver = "silver"


class GuestStatus(str, Enum):
    checked_in = "checked_in"
    pre_arrival = "pre_arrival"


class RequestCategory(str, Enum):
    housekeeping = "housekeeping"
    dining = "dining"
    maintenance = "maintenance"
    concierge = "concierge"
    front_desk = "front_desk"
    other = "other"


class RequestPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RequestStatus(str, Enum):
    new = "new"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"


# Status transitions for staff updates (new → assigned → in_progress → completed)
VALID_TRANSITIONS: dict[str, list[str]] = {
    "new": ["assigned"],
    "assigned": ["in_progress"],
    "in_progress": ["completed"],
    "completed": [],
}


# -----------------------------------------------------------------------------
# Tables
# -----------------------------------------------------------------------------
class Guest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    confirmation_code: str = Field(unique=True, index=True)
    tier: GuestTier = GuestTier.silver
    status: GuestStatus = GuestStatus.checked_in
    room_number: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    service_requests: list["ServiceRequest"] = Relationship(back_populates="guest")


class StaffUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    role: str = "staff"

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ServiceRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    guest_id: int = Field(foreign_key="guest.id")
    category: RequestCategory
    priority: RequestPriority = RequestPriority.medium
    request_type: str | None = None  # Selected subtype (e.g. "Late checkout")
    description: str = ""  # Optional extra details (empty when none added)
    status: RequestStatus = RequestStatus.new
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    guest: Guest | None = Relationship(back_populates="service_requests")
    activities: list["RequestActivity"] = Relationship(back_populates="request")


class RequestActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="servicerequest.id")
    action: str
    staff_name: str | None = None
    note: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    request: ServiceRequest | None = Relationship(back_populates="activities")
