from fastapi import FastAPI

from prcp.api.schemas import HealthOut, ReadyOut, ServiceCreate, ServiceOut
from prcp.models import create_service
from prcp.repository import InMemoryServiceRepository

app = FastAPI(title="Platform Reliability Control Plane")
service_repository = InMemoryServiceRepository()


@app.get("/health")
def health() -> HealthOut:
    return HealthOut(status="ok")


@app.get("/ready")
def ready() -> ReadyOut:
    return ReadyOut(status="ready")


@app.post("/services")
def create_service_endpoint(request: ServiceCreate) -> ServiceOut:
    service = create_service(service_name=request.name, service_url=request.url)
    service_repository.save(service=service)
    return ServiceOut(name=service.name, url=service.url)
