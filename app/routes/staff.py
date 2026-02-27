# app/routes/staff.py — Staff-facing routes (prefix /staff)
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import require_staff
from app.database import get_session
from app.models import Guest, RequestActivity, RequestCategory, RequestPriority, RequestStatus, ServiceRequest, StaffUser, VALID_TRANSITIONS

router = APIRouter(prefix="/staff", tags=["staff"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))


def _filtered_requests(
    session: Session,
    status_filter: str | None = None,
    category_filter: str | None = None,
    search: str | None = None,
) -> list[ServiceRequest]:
    statement = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.guest))
        .join(Guest)
    )
    if status_filter:
        statement = statement.where(ServiceRequest.status == status_filter)
    if category_filter:
        statement = statement.where(ServiceRequest.category == category_filter)
    if search and search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(
            (ServiceRequest.description.ilike(term))
            | (Guest.first_name.ilike(term))
            | (Guest.last_name.ilike(term))
        )
    statement = statement.order_by(ServiceRequest.created_at.desc())
    return list(session.exec(statement).all())


@router.get("", response_class=HTMLResponse)
async def staff_dashboard(
    request: Request,
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
    status_filter: str | None = None,
    category_filter: str | None = None,
    search: str | None = None,
):
    requests_list = _filtered_requests(session, status_filter, category_filter, search)
    return templates.TemplateResponse(
        request,
        "staff/dashboard.html",
        context={
            "requests": requests_list,
            "staff": staff,
            "is_staff": True,
            "status_filter": status_filter or "",
            "category_filter": category_filter or "",
            "search": search or "",
        },
    )


@router.get("/requests/filter", response_class=HTMLResponse)
async def staff_filter(
    request: Request,
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
    status_filter: str | None = None,
    category_filter: str | None = None,
    search: str | None = None,
):
    requests_list = _filtered_requests(session, status_filter, category_filter, search)
    return templates.TemplateResponse(
        request,
        "_partials/staff_requests_table.html",
        context={"requests": requests_list, "is_staff": True},
    )


@router.get("/requests/{request_id}", response_class=HTMLResponse)
async def request_detail(
    request: Request,
    request_id: int,
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
    error: str | None = None,
):
    sr = session.exec(
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.guest))
        .where(ServiceRequest.id == request_id)
    ).first()
    if not sr:
        return RedirectResponse("/staff", status_code=303)
    activities = session.exec(
        select(RequestActivity)
        .where(RequestActivity.request_id == request_id)
        .order_by(RequestActivity.created_at.asc())
    ).all()
    next_statuses = VALID_TRANSITIONS.get(sr.status.value, [])
    return templates.TemplateResponse(
        request,
        "staff/request_detail.html",
        context={
            "sr": sr,
            "activities": activities,
            "staff": staff,
            "next_statuses": next_statuses,
            "error": error,
        },
    )


@router.post("/requests/{request_id}/status")
async def update_status(
    request: Request,
    request_id: int,
    status: str = Form(...),
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
):
    sr = session.exec(
        select(ServiceRequest).where(ServiceRequest.id == request_id)
    ).first()
    if not sr:
        return RedirectResponse("/staff", status_code=303)

    allowed = VALID_TRANSITIONS.get(sr.status.value, [])
    if status not in allowed:
        return await request_detail(request, request_id, staff, session, error="Invalid status transition.")

    old_status = sr.status.value
    sr.status = RequestStatus(status)
    sr.updated_at = datetime.now(UTC)
    session.add(sr)

    activity = RequestActivity(
        request_id=sr.id,
        action=f"Status changed from {old_status} to {status}",
        staff_name=staff.name,
    )
    session.add(activity)
    session.commit()

    return RedirectResponse(f"/staff/requests/{request_id}", status_code=303)
