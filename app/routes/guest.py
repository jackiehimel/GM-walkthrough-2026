# app/routes/guest.py — Guest-facing routes (prefix /guest)
import json
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
    return templates.TemplateResponse(
        request, "guest/home.html",
        context={"guest": guest},
    )


def _guest_requests(session: Session, guest_id: int) -> list[ServiceRequest]:
    statement = (
        select(ServiceRequest)
        .where(ServiceRequest.guest_id == guest_id)
        .order_by(ServiceRequest.created_at.desc())
    )
    return list(session.exec(statement).all())


@router.get("/requests", response_class=HTMLResponse)
async def my_requests(
    request: Request,
    guest: Guest = Depends(get_current_guest),
    session: Session = Depends(get_session),
):
    requests_list = _guest_requests(session, guest.id)
    return templates.TemplateResponse(
        request,
        "guest/my_requests.html",
        context={"requests": requests_list, "is_staff": False},
    )


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
    request_type: str | None = None,
):
    preselect_category = category
    preselect_request_type = request_type
    return templates.TemplateResponse(
        request,
        "guest/submit_request.html",
        context={
            "category_options": CATEGORY_OPTIONS,
            "category_options_json": json.dumps(CATEGORY_OPTIONS),
            "preselect_category": preselect_category,
            "preselect_request_type": preselect_request_type,
        },
    )


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
    if not _description_required_for_category(category, description):
        return templates.TemplateResponse(
            request,
            "guest/submit_request.html",
            context={
                "category_options": CATEGORY_OPTIONS,
                "category_options_json": json.dumps(CATEGORY_OPTIONS),
                "preselect_category": category,
                "preselect_request_type": request_type,
                "error": "Description is required when category is Other.",
            },
        )
    try:
        req_category = RequestCategory(category)
        req_priority = RequestPriority(priority)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "guest/submit_request.html",
            context={
                "category_options": CATEGORY_OPTIONS,
                "category_options_json": json.dumps(CATEGORY_OPTIONS),
                "preselect_category": category,
                "preselect_request_type": request_type,
                "error": "Invalid category or priority.",
            },
        )
    sr = ServiceRequest(
        guest_id=guest.id,
        category=req_category,
        priority=req_priority,
        request_type=request_type.strip() if (request_type and request_type.strip()) else None,
        description=(description or "").strip(),
        status=RequestStatus.new,
    )
    session.add(sr)
    session.commit()
    session.refresh(sr)
    return RedirectResponse("/guest/requests", status_code=303)
