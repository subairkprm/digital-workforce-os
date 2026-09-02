from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    tenant_id: str
    permissions: list[str]


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: Optional[str] = Field(default=None, max_length=500)


class DepartmentPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    description: Optional[str] = Field(default=None, max_length=500)


class DepartmentOut(ORMModel):
    id: str
    name: str
    description: Optional[str]


class EmployeeCreate(BaseModel):
    employee_number: str = Field(min_length=1, max_length=80)
    full_name: str = Field(min_length=1, max_length=160)
    work_email: EmailStr
    title: Optional[str] = Field(default=None, max_length=160)
    department_id: Optional[str] = None


class EmployeePatch(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=160)
    work_email: Optional[EmailStr] = None
    title: Optional[str] = Field(default=None, max_length=160)
    department_id: Optional[str] = None


class EmployeeOut(ORMModel):
    id: str
    employee_number: str
    full_name: str
    work_email: EmailStr
    title: Optional[str]
    department_id: Optional[str]
    is_suspended: bool


class AuditOut(ORMModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, object]
    created_at: datetime


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    permissions: list[str] = Field(default_factory=list, max_length=30)


class RolePatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    permissions: Optional[list[str]] = Field(default=None, max_length=30)


class RoleOut(BaseModel):
    id: str
    name: str
    permissions: list[str]


class MembershipRoleUpdate(BaseModel):
    role_ids: list[str] = Field(max_length=30)


class MembershipOut(BaseModel):
    id: str
    user_id: str
    role_ids: list[str]


class SecurityEventOut(BaseModel):
    id: str
    category: str
    outcome: str
    metadata: dict[str, object]
    created_at: datetime
