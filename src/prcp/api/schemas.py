from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


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
