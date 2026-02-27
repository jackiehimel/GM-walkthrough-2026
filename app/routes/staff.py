# app/routes/staff.py — Staff-facing routes (prefix /staff)
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import require_staff
from app.database import get_session
from app.models import Guest, RequestActivity, RequestCategory, RequestPriority, RequestStatus, ServiceRequest, StaffUser

router = APIRouter(prefix="/staff", tags=["staff"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))


@router.get("", response_class=HTMLResponse)
async def staff_dashboard(
    request: Request,
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
):
    statement = (
        select(ServiceRequest)
        .options(selectinload(ServiceRequest.guest))
        .order_by(ServiceRequest.created_at.desc())
    )
    requests_list = list(session.exec(statement).all())
    return templates.TemplateResponse(
        request,
        "staff/dashboard.html",
        context={"requests": requests_list, "staff": staff, "is_staff": True},
    )


@router.get("/requests/{request_id}", response_class=HTMLResponse)
async def request_detail(
    request: Request,
    request_id: int,
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
):
    # TODO: Render request detail with full info and activity timeline
    return HTMLResponse("TODO")


@router.post("/requests/{request_id}/status")
async def update_status(
    request: Request,
    request_id: int,
    status: str = Form(...),
    staff: StaffUser = Depends(require_staff),
    session: Session = Depends(get_session),
):
    # TODO: Update request status, add RequestActivity, redirect to request detail
    return HTMLResponse("TODO")
