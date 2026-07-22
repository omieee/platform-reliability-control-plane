from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120, title="Service Name")
    url: HttpUrl = Field(title="Service URL")

    @field_validator("name")
    @classmethod
    def valid_service_name(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("name cannot be empty")
        return stripped_value.lower()


class HealthOut(BaseModel):
    status: str


class ReadyOut(BaseModel):
    status: str


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    url: HttpUrl
