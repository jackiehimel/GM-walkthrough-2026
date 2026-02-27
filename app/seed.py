# app/seed.py — Seed database with demo data from seed_data/seed.json
import json
from pathlib import Path

from sqlmodel import Session, select

from app.database import engine
from app.models import (
    Guest,
    GuestStatus,
    GuestTier,
    RequestActivity,
    RequestCategory,
    RequestPriority,
    RequestStatus,
    ServiceRequest,
    StaffUser,
)


def load_seed_data() -> dict:
    # Load seed.json; expects keys: guests, staff, service_requests.
    path = Path(__file__).parent.parent / "seed_data" / "seed.json"
    with open(path) as f:
        return json.load(f)


def seed():
    # Populate DB with demo data. No-op if guests already exist.
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if session.exec(select(Guest)).first():
            print("Database already seeded, skipping.")
            return

        data = load_seed_data()

        guests: list[Guest] = []
        for g in data["guests"]:
            guest = Guest(
                first_name=g["first_name"],
                last_name=g["last_name"],
                confirmation_code=g["confirmation_code"],
                tier=GuestTier(g["tier"]),
                status=GuestStatus(g["status"]),
                room_number=g.get("room_number"),
            )
            session.add(guest)
            session.flush()
            guests.append(guest)

        for s in data["staff"]:
            session.add(
                StaffUser(
                    employee_id=s["employee_id"],
                    first_name=s["first_name"],
                    last_name=s["last_name"],
                    role=s["role"],
                )
            )

        staff_names = [f"{s['first_name']} {s['last_name']}" for s in data["staff"]]
        for req in data["service_requests"]:
            guest = guests[req["guest_index"]]
            sr = ServiceRequest(
                guest_id=guest.id,
                category=RequestCategory(req["category"]),
                priority=RequestPriority(req["priority"]),
                request_type=req.get("request_type"),
                description=req.get("description", ""),
                status=RequestStatus(req["status"]),
            )
            session.add(sr)
            session.flush()
            session.add(
                RequestActivity(
                    request_id=sr.id,
                    action="created",
                    note="Request submitted by guest",
                )
            )
            if req["status"] != "new":
                staff_idx = 1 if req["status"] == "in_progress" and len(staff_names) > 1 else 0
                staff_name = staff_names[staff_idx] if staff_names else None
                session.add(
                    RequestActivity(
                        request_id=sr.id,
                        action=req["status"],
                        note=f"Status updated to {req['status']}",
                        staff_name=staff_name,
                    )
                )

        session.commit()
        print("Seed data loaded successfully.")


if __name__ == "__main__":
    seed()
