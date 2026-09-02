from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import get_settings
from app.database import get_db
from app.dependencies import RequestContext, require_permission
from app.models import Department
from app.rate_limit import enforce_rate_limit
from app.schemas import DepartmentCreate, DepartmentOut, DepartmentPatch

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentOut])
def list_departments(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.read"))],
) -> list[Department]:
    return list(db.scalars(select(Department).where(Department.tenant_id == context.tenant_id)))


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("department.manage"))],
) -> Department:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    department = Department(tenant_id=context.tenant_id, **payload.model_dump())
    db.add(department)
    db.flush()
    record_audit(db, context, "department.created", "department", department.id)
    db.commit()
    db.refresh(department)
    return department


@router.patch("/{department_id}", response_model=DepartmentOut)
def update_department(
    department_id: str,
    payload: DepartmentPatch,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("department.manage"))],
) -> Department:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    department = db.scalar(
        select(Department).where(
            Department.id == department_id, Department.tenant_id == context.tenant_id
        )
    )
    if department is None:
        raise HTTPException(status_code=404, detail="department not found")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(department, field, value)
    record_audit(
        db, context, "department.updated", "department", department.id, {"fields": list(changes)}
    )
    db.commit()
    db.refresh(department)
    return department
