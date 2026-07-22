from fastapi import FastAPI, HTTPException, status

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
    service = create_service(service_name=request.name, service_url=str(request.url))
    service_repository.save(service=service)
    return ServiceOut.model_validate(service)


@app.get("/services", response_model=list[ServiceOut], status_code=status.HTTP_200_OK)
def get_all_services() -> list[ServiceOut]:
    services = service_repository.list_all()
    return [ServiceOut.model_validate(service) for service in services]


@app.get(
    "/services/{service_name}",
    response_model=ServiceOut,
    status_code=status.HTTP_200_OK,
)
def get_service(service_name: str) -> ServiceOut:
    service = service_repository.get_by_name(service_name=service_name)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return ServiceOut.model_validate(service)
