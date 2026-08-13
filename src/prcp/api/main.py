from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status

from prcp.api.dependencies import (
    get_environment_repository,
    get_probe_repository,
    get_probe_result_repository,
    get_service_repository,
)
from prcp.api.errors import register_error_handlers
from prcp.api.schemas import (
    EnvironmentCreate,
    EnvironmentOut,
    HealthOut,
    ProbeCreate,
    ProbeOut,
    ProbeResultOut,
    ReadyOut,
    ServiceCreate,
    ServiceOut,
)
from prcp.checker import http_check
from prcp.models import create_environment, create_http_probe, create_service
from prcp.repository import (
    EnvironmentRepository,
    ProbeRepository,
    ProbeResultRepository,
    ServiceRepository,
)

app = FastAPI(title="Platform Reliability Control Plane")
register_error_handlers(app)


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok")


@app.get("/ready", response_model=ReadyOut)
def ready() -> ReadyOut:
    return ReadyOut(status="ready")


### SERVICE RELATED ROUTES


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


### Environment Related Routes


@app.post(
    "/environments", response_model=EnvironmentOut, status_code=status.HTTP_201_CREATED
)
def create_environment_endpoint(
    request: EnvironmentCreate,
    repository: Annotated[EnvironmentRepository, Depends(get_environment_repository)],
) -> EnvironmentOut:
    environment = create_environment(
        environment_name=request.name, region=request.region, cluster=request.cluster
    )
    repository.save(environment=environment)
    return EnvironmentOut.model_validate(environment)


@app.get(
    "/environments", response_model=list[EnvironmentOut], status_code=status.HTTP_200_OK
)
def get_all_environments(
    repository: Annotated[
        EnvironmentRepository,
        Depends(get_environment_repository),
    ],
) -> list[EnvironmentOut]:
    environments = repository.list_all()
    return [EnvironmentOut.model_validate(env) for env in environments]


@app.get(
    "/environments/{environment_name}",
    response_model=EnvironmentOut,
    status_code=status.HTTP_200_OK,
)
def get_environment(
    environment_name: str,
    repository: Annotated[
        EnvironmentRepository,
        Depends(get_environment_repository),
    ],
) -> EnvironmentOut:
    environment = repository.get_by_name(environment_name=environment_name)
    if environment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Environment not found"
        )
    return EnvironmentOut.model_validate(environment)


### Probe Related Routes
@app.post(
    "/probes",
    response_model=ProbeOut,
    status_code=status.HTTP_201_CREATED,
)
def register_probe(
    request: ProbeCreate,
    service_repository: Annotated[
        ServiceRepository,
        Depends(get_service_repository),
    ],
    environment_repository: Annotated[
        EnvironmentRepository,
        Depends(get_environment_repository),
    ],
    probe_repository: Annotated[
        ProbeRepository,
        Depends(get_probe_repository),
    ],
) -> ProbeOut:
    service = service_repository.get_by_name(request.service_name)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{request.service_name}' not found",
        )

    environment = environment_repository.get_by_name(request.environment_name)

    if environment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment '{request.environment_name}' not found",
        )

    probe = create_http_probe(
        environment=environment,
        service=service,
        method=request.method,
        path=request.path,
        expected_status_code=request.expected_status_code,
        timeout_seconds=request.timeout_seconds,
    )

    probe_repository.save(probe)

    return ProbeOut(
        id=probe.id,
        service_name=probe.service.name,
        environment_name=probe.environment.name,
        method=probe.method,
        path=probe.path,
        expected_status_code=probe.expected_status_code,
        timeout_seconds=probe.timeout_seconds,
    )


### Probe relult related routes
@app.post(
    "/probes/{probe_id}/run",
    response_model=ProbeResultOut,
    status_code=status.HTTP_200_OK,
)
def run_probe(
    probe_id: UUID,
    probe_repository: Annotated[
        ProbeRepository,
        Depends(get_probe_repository),
    ],
    result_repository: Annotated[
        ProbeResultRepository,
        Depends(get_probe_result_repository),
    ],
) -> ProbeResultOut:
    probe = probe_repository.get_by_id(probe_id)

    if probe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe '{probe_id}' not found",
        )

    result = http_check(probe)

    result_repository.add(result)

    return ProbeResultOut(
        probe_id=result.probe.id,
        status=result.status,
        actual_status_code=result.actual_status_code,
        failure_reason=result.failure_reason,
        latency_ms=result.latency_ms,
    )


@app.get(
    "/probes/{probe_id}/results",
    response_model=list[ProbeResultOut],
)
def get_probe_results(
    probe_id: UUID,
    probe_repository: Annotated[
        ProbeRepository,
        Depends(get_probe_repository),
    ],
    result_repository: Annotated[
        ProbeResultRepository,
        Depends(get_probe_result_repository),
    ],
) -> list[ProbeResultOut]:
    probe = probe_repository.get_by_id(probe_id)

    if probe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe '{probe_id}' not found",
        )

    results = result_repository.list_for_probe(probe_id)

    return [
        ProbeResultOut(
            probe_id=result.probe.id,
            status=result.status,
            actual_status_code=result.actual_status_code,
            failure_reason=result.failure_reason,
            latency_ms=result.latency_ms,
        )
        for result in results
    ]
