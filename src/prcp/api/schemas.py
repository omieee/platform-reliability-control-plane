from pydantic import BaseModel, Field, field_validator

from prcp.models import Service
from prcp.repository import InMemoryServiceRepository


class HealthOut(BaseModel):
    status: str


class ReadyOut(BaseModel):
    ready: str


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, title="Service Name")
    url: str = Field(min_length=1, title="Service URL")

    @field_validator("url")
    def valid_url(u):
        if u.startswith(("http://", "https://")):
            return u
        else:
            raise ValueError("Service URL must start with http or https")

    def create_service(self) -> Service | None:
        serv = Service(self.name, self.url)
        repo = InMemoryServiceRepository()
        repo.save(service=serv)
        return repo.get_by_name(service_name=self.name)
