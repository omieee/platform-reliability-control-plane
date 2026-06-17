from fastapi import FastAPI, status

from prcp.api.schemas import HealthOut, ReadyOut, ServiceCreate, ServiceOut
from prcp.models import create_service
from prcp.repository import InMemoryServiceRepository

app = FastAPI(title="Platform Reliability Control Plane")
service_repository = InMemoryServiceRepository()


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok")


@app.get("/ready", response_model=ReadyOut)
def ready() -> ReadyOut:
    return ReadyOut(status="ready")


@app.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service_endpoint(request: ServiceCreate) -> ServiceOut:
    service = create_service(service_name=request.name, service_url=request.url)
    service_repository.save(service=service)
    return ServiceOut(name=service.name, url=service.url)
