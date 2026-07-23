from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from prcp.api.dependencies import get_service_repository
from prcp.api.schemas import HealthOut, ReadyOut, ServiceCreate, ServiceOut
from prcp.exceptions import DuplicateServiceException
from prcp.models import create_service
from prcp.repository import ServiceRepository

app = FastAPI(title="Platform Reliability Control Plane")


@app.exception_handler(DuplicateServiceException)
async def duplicate_service_handler(request: Request, exc: DuplicateServiceException):
    return JSONResponse(
        status_code=409,
        content={
            "message": f"Oops! {exc.service_name} already exist",
            "resolution": "Use different name for the service",
        },
    )


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok")


@app.get("/ready", response_model=ReadyOut)
def ready() -> ReadyOut:
    return ReadyOut(status="ready")


@app.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def create_service_endpoint(
    request: ServiceCreate,
    repository: Annotated[ServiceRepository, Depends(get_service_repository)],
) -> ServiceOut:
    service = create_service(service_name=request.name, service_url=str(request.url))
    repository.save(service=service)
    return ServiceOut.model_validate(service)


@app.get("/services", response_model=list[ServiceOut], status_code=status.HTTP_200_OK)
def get_all_services(
    repository: Annotated[
        ServiceRepository,
        Depends(get_service_repository),
    ],
) -> list[ServiceOut]:
    services = repository.list_all()
    return [ServiceOut.model_validate(service) for service in services]


@app.get(
    "/services/{service_name}",
    response_model=ServiceOut,
    status_code=status.HTTP_200_OK,
)
def get_service(
    service_name: str,
    repository: Annotated[
        ServiceRepository,
        Depends(get_service_repository),
    ],
) -> ServiceOut:
    service = repository.get_by_name(service_name=service_name)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service not found"
        )
    return ServiceOut.model_validate(service)
