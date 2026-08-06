from http import HTTPMethod, HTTPStatus
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from prcp.helpers import normalize_name


class HealthOut(BaseModel):
    status: str


class ReadyOut(BaseModel):
    status: str


class ServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120, title="Service Name")
    url: HttpUrl = Field(title="Service URL")

    @field_validator("name")
    @classmethod
    def valid_service_name(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("name cannot be empty")
        return stripped_value.lower()


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    url: HttpUrl


class EnvironmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120, title="Environment Name")
    region: str = Field(min_length=1, max_length=120, title="Region Name")
    cluster: str = Field(min_length=1, max_length=1000, title="Cluster Name")

    @field_validator("name")
    @classmethod
    def valid_env_name(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("name cannot be empty")
        return stripped_value.lower()


class EnvironmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    region: str
    cluster: str


class ProbeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str
    environment_name: str
    method: HTTPMethod = HTTPMethod.GET
    path: str
    expected_status_code: HTTPStatus = HTTPStatus.OK
    timeout_seconds: float = Field(default=2.0, gt=0)

    @field_validator("service_name", "environment_name")
    @classmethod
    def normalize_reference_names(cls, value: str) -> str:
        normalized_name = normalize_name(value)
        if not normalized_name:
            raise ValueError("name cannot be empty")
        return normalized_name


class ProbeOut(BaseModel):
    id: UUID
    service_name: str
    environment_name: str
    method: HTTPMethod
    path: str
    expected_status_code: int
    timeout_seconds: float
