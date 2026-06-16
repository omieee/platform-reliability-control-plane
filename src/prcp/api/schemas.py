from pydantic import BaseModel, Field, field_validator


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, title="Service Name")
    url: str = Field(min_length=1, title="Service URL")

    @field_validator("name")
    @classmethod
    def valid_service_name(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("name cannot be empty")
        else:
            return stripped_value

    @field_validator("url")
    @classmethod
    def valid_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("Service URL must start with http or https")
        else:
            return value


class HealthOut(BaseModel):
    status: str


class ReadyOut(BaseModel):
    status: str


class ServiceOut(BaseModel):
    name: str
    url: str
