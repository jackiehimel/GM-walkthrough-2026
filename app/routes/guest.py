# app/routes/guest.py — Guest-facing routes (prefix /guest)
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.auth import get_current_guest
from app.database import get_session
from app.models import Guest, RequestCategory, RequestPriority, RequestStatus, ServiceRequest

router = APIRouter(prefix="/guest", tags=["guest"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))


@router.get("", response_class=HTMLResponse)
async def guest_home(
    request: Request,
    guest: Guest = Depends(get_current_guest),
):
    # TODO: Render guest home with welcome message and quick-action tiles
    return HTMLResponse("TODO")


def _guest_requests(session, guest_id):
    # TODO: Fetch all ServiceRequests for guest, newest first
    pass


@router.get("/requests", response_class=HTMLResponse)
async def my_requests(
    request: Request,
    guest: Guest = Depends(get_current_guest),
    session: Session = Depends(get_session),
):
    # TODO: Render guest's request list (status, category, priority, time)
    return HTMLResponse("TODO")


CATEGORY_OPTIONS = {
    "housekeeping": ["Extra towels", "Room cleaning", "Amenity refill"],
    "dining": ["Room service", "Restaurant reservation", "Special dietary request"],
    "maintenance": ["AC/heating issue", "Plumbing", "Lighting"],
    "concierge": ["Transportation", "Event tickets", "Local recommendations"],
    "front_desk": ["Late checkout", "Room change", "Billing question"],
    "other": ["Other"],  # Description required when category is "other"
}


@router.get("/requests/new", response_class=HTMLResponse)
async def submit_request_form(
    request: Request,
    guest: Guest = Depends(get_current_guest),
    category: str | None = None,
):
    # TODO: Render submit request form with category, priority, description fields
    return HTMLResponse("TODO")


def _description_required_for_category(category: str, description: str) -> bool:
    """Return True if description is valid. When category is 'other', description must be non-empty."""
    if category == "other":
        return bool(description and description.strip())
    return True


@router.post("/requests")
async def create_request(
    request: Request,
    guest: Guest = Depends(get_current_guest),
    session: Session = Depends(get_session),
    category: str = Form(...),
    priority: str = Form("medium"),
    request_type: str | None = Form(None),
    description: str = Form(""),
):
    # TODO: Create ServiceRequest, add RequestActivity, redirect to /guest/requests
    # Validation: when category is "other", description is required (use _description_required_for_category)
    return HTMLResponse("TODO")
