from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.identity.validators import validate_country_code, validate_employee_id, validate_phone_number


class PaginationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    search: str | None = None
    status: str | None = None
    organization_id: UUID | None = None
    department_id: UUID | None = None
    team_id: UUID | None = None


class TenantCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    configuration: dict[str, object] = Field(default_factory=dict)
    tenant_metadata: dict[str, object] = Field(default_factory=dict)


class TenantUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    configuration: dict[str, object] | None = None
    tenant_metadata: dict[str, object] | None = None


class OrganizationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    legal_name: str | None = None
    description: str | None = None
    logo_url: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    organization_metadata: dict[str, object] = Field(default_factory=dict)
    organization_settings: dict[str, object] = Field(default_factory=dict)


class OrganizationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    legal_name: str | None = None
    status: str | None = None
    description: str | None = None
    logo_url: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    organization_metadata: dict[str, object] | None = None
    organization_settings: dict[str, object] | None = None


class DepartmentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: UUID
    code: str
    name: str
    status: str = "active"
    manager_user_id: UUID | None = None
    department_metadata: dict[str, object] = Field(default_factory=dict)
    department_settings: dict[str, object] = Field(default_factory=dict)


class DepartmentUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    manager_user_id: UUID | None = None
    department_metadata: dict[str, object] | None = None
    department_settings: dict[str, object] | None = None


class TeamCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    department_id: UUID
    code: str
    name: str
    status: str = "active"
    lead_user_id: UUID | None = None
    team_metadata: dict[str, object] = Field(default_factory=dict)
    team_settings: dict[str, object] = Field(default_factory=dict)


class TeamUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    status: str | None = None
    lead_user_id: UUID | None = None
    team_metadata: dict[str, object] | None = None
    team_settings: dict[str, object] | None = None


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    username: str
    display_name: str
    tenant_id: UUID | None = None
    organization_id: UUID | None = None
    department_id: UUID | None = None
    team_id: UUID | None = None
    employee_id: str | None = None
    designation: str | None = None
    status: str = "active"
    phone_number: str | None = None
    profile_picture_url: str | None = None

    @field_validator("phone_number")
    @classmethod
    def _validate_phone_number(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @field_validator("employee_id")
    @classmethod
    def _validate_employee_id(cls, value: str | None) -> str | None:
        return validate_employee_id(value)


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = None
    status: str | None = None
    phone_number: str | None = None
    designation: str | None = None
    organization_id: UUID | None = None
    department_id: UUID | None = None
    team_id: UUID | None = None
    profile_picture_url: str | None = None
    employee_id: str | None = None

    @field_validator("phone_number")
    @classmethod
    def _validate_phone_number(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @field_validator("employee_id")
    @classmethod
    def _validate_employee_id(cls, value: str | None) -> str | None:
        return validate_employee_id(value)


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    country: str | None = None
    phone_number: str | None = None
    profile_picture_url: str | None = None
    timezone: str | None = None
    language: str | None = None
    theme: str | None = None
    dashboard_layout: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    personal_information: dict[str, object] | None = None
    contact_information: dict[str, object] | None = None
    employment_information: dict[str, object] | None = None
    accessibility_preferences: dict[str, object] | None = None

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def _validate_phone_number(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @field_validator("country")
    @classmethod
    def _validate_country(cls, value: str | None) -> str | None:
        return validate_country_code(value)


class PreferenceUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    theme: str | None = None
    language: str | None = None
    timezone: str | None = None
    dashboard_layout: str | None = None
    notification_preferences: dict[str, object] | None = None
    security_preferences: dict[str, object] | None = None
    accessibility_preferences: dict[str, object] | None = None


class TenantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    status: str
    configuration: dict[str, object]
    tenant_metadata: dict[str, object]
    activated_at: datetime | None
    suspended_at: datetime | None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    legal_name: str | None
    description: str | None
    logo_url: str | None
    contact_email: str | None
    contact_phone: str | None
    status: str
    organization_metadata: dict[str, object]
    organization_settings: dict[str, object]
    created_at: datetime
    updated_at: datetime


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    organization_id: UUID
    code: str
    name: str
    status: str
    manager_user_id: UUID | None
    department_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class TeamResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    department_id: UUID
    code: str
    name: str
    status: str
    lead_user_id: UUID | None
    team_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    organization_id: UUID | None
    department_id: UUID | None
    team_id: UUID | None
    email: str
    username: str
    employee_id: str | None
    designation: str | None
    display_name: str
    phone_number: str | None
    status: str
    profile_picture_url: str | None
    last_login_at: datetime | None
    last_activity_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    user_id: UUID
    first_name: str | None
    last_name: str | None
    full_name: str | None
    country: str | None
    phone_number: str | None
    profile_picture_url: str | None
    timezone: str | None
    language: str | None
    theme: str | None
    dashboard_layout: str | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    personal_information: dict[str, object]
    contact_information: dict[str, object]
    employment_information: dict[str, object]
    accessibility_preferences: dict[str, object]


class UserPreferenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    user_id: UUID
    theme: str | None
    language: str | None
    timezone: str | None
    dashboard_layout: str | None
    notification_preferences: dict[str, object]
    security_preferences: dict[str, object]
    accessibility_preferences: dict[str, object]


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    user_id: UUID
    employee_id: str
    designation: str | None
    department_id: UUID | None
    team_id: UUID | None
    manager_user_id: UUID | None
    hire_date: datetime | None
    employment_status: str
    employee_metadata: dict[str, object]


class DirectoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    entity_type: str
    entity_id: UUID
    display_name: str
    email: str | None
    organization_name: str | None
    department_name: str | None
    team_name: str | None
    status: str
    role_codes: list[str]
    directory_metadata: dict[str, object]


class PageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[dict[str, object]]
    total: int
    page: int
    page_size: int

