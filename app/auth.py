# app/auth.py — Authentication helpers (lookup + FastAPI dependencies)
from fastapi import Depends, Request
from sqlmodel import Session, select

from app.database import get_session
from app.models import Guest, StaffUser


def lookup_staff(
    session: Session, employee_id: str, last_name: str
) -> StaffUser | None:
    # Find staff by employee_id and last_name (case-insensitive). Returns None if not found.
    return session.exec(
        select(StaffUser).where(
            StaffUser.employee_id == employee_id,
            StaffUser.last_name.ilike(last_name),
        )
    ).first()


def lookup_guest(
    session: Session, confirmation_code: str, last_name: str
) -> Guest | None:
    # Find guest by confirmation_code and last_name (case-insensitive). Returns None if not found.
    return session.exec(
        select(Guest).where(
            Guest.confirmation_code == confirmation_code,
            Guest.last_name.ilike(last_name),
        )
    ).first()


async def get_current_guest(
    request: Request,
    session: Session = Depends(get_session),
) -> Guest:
    # FastAPI dependency: require guest session. Redirects to /login if not logged in or guest not found.
    guest_id = request.session.get("guest_id")
    if not guest_id:
        raise _redirect_exception("/login")
    guest = session.get(Guest, guest_id)
    if not guest:
        request.session.clear()
        raise _redirect_exception("/login")
    return guest


async def require_staff(
    request: Request,
    session: Session = Depends(get_session),
) -> StaffUser:
    # FastAPI dependency: require staff session. Redirects to /staff/login if not logged in or staff not found.
    staff_id = request.session.get("staff_id")
    if not staff_id:
        raise _redirect_exception("/staff/login")
    staff = session.get(StaffUser, staff_id)
    if not staff:
        request.session.clear()
        raise _redirect_exception("/staff/login")
    return staff


class _RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url


def _redirect_exception(url: str) -> _RedirectException:
    return _RedirectException(url)
