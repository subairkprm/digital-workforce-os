from __future__ import annotations

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import get_settings
from app.database import get_db
from app.dependencies import Context, RequestContext, require_permission
from app.models import Department, Employee, Membership
from app.rate_limit import enforce_rate_limit
from app.schemas import EmployeeCreate, EmployeeOut, EmployeePatch

router = APIRouter(prefix="/employees", tags=["employees"])


def _department_valid(db: Session, tenant_id: str, department_id: Optional[str]) -> bool:
    return (
        department_id is None
        or db.scalar(
            select(Department.id).where(
                Department.id == department_id, Department.tenant_id == tenant_id
            )
        )
        is not None
    )


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.create"))],
) -> Employee:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    if not _department_valid(db, context.tenant_id, payload.department_id):
        raise HTTPException(status_code=422, detail="invalid department")
    employee = Employee(tenant_id=context.tenant_id, **payload.model_dump())
    db.add(employee)
    db.flush()
    record_audit(db, context, "employee.created", "employee", employee.id)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("", response_model=list[EmployeeOut])
def list_employees(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.read"))],
    q: Annotated[Optional[str], Query(max_length=160)] = None,
    suspended: Optional[bool] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[Employee]:
    query = select(Employee).where(Employee.tenant_id == context.tenant_id)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Employee.full_name.ilike(pattern),
                Employee.work_email.ilike(pattern),
                Employee.employee_number.ilike(pattern),
            )
        )
    if suspended is not None:
        query = query.where(Employee.is_suspended.is_(suspended))
    query = query.order_by(Employee.full_name, Employee.id).offset(offset).limit(limit)
    return list(db.scalars(query))


@router.get("/me", response_model=EmployeeOut)
def get_my_employee_profile(
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> Employee:
    employee = db.scalar(
        select(Employee).where(
            Employee.user_id == context.user.id,
            Employee.tenant_id == context.tenant_id,
        )
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="employee profile not found")
    return employee


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.read"))],
) -> Employee:
    employee = db.scalar(
        select(Employee).where(Employee.id == employee_id, Employee.tenant_id == context.tenant_id)
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: str,
    payload: EmployeePatch,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.update"))],
) -> Employee:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    employee = db.scalar(
        select(Employee).where(Employee.id == employee_id, Employee.tenant_id == context.tenant_id)
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    changes = payload.model_dump(exclude_unset=True)
    if "department_id" in changes and not _department_valid(
        db, context.tenant_id, changes["department_id"]
    ):
        raise HTTPException(status_code=422, detail="invalid department")
    for field, value in changes.items():
        setattr(employee, field, value)
    record_audit(
        db, context, "employee.updated", "employee", employee.id, {"fields": list(changes)}
    )
    db.commit()
    db.refresh(employee)
    return employee


@router.post("/{employee_id}/suspend", response_model=EmployeeOut)
def suspend_employee(
    employee_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.suspend"))],
) -> Employee:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    employee = db.scalar(
        select(Employee).where(Employee.id == employee_id, Employee.tenant_id == context.tenant_id)
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    employee.is_suspended = True
    if employee.user_id is not None:
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == employee.user_id,
                Membership.tenant_id == context.tenant_id,
            )
        )
        if membership is not None:
            membership.is_active = False
    record_audit(db, context, "employee.suspended", "employee", employee.id)
    db.commit()
    db.refresh(employee)
    return employee


@router.post("/{employee_id}/reactivate", response_model=EmployeeOut)
def reactivate_employee(
    employee_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.suspend"))],
) -> Employee:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    employee = db.scalar(
        select(Employee).where(Employee.id == employee_id, Employee.tenant_id == context.tenant_id)
    )
    if employee is None:
        raise HTTPException(status_code=404, detail="employee not found")
    employee.is_suspended = False
    if employee.user_id is not None:
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == employee.user_id,
                Membership.tenant_id == context.tenant_id,
            )
        )
        if membership is not None:
            membership.is_active = True
    record_audit(db, context, "employee.reactivated", "employee", employee.id)
    db.commit()
    db.refresh(employee)
    return employee
