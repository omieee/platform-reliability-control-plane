from fastapi import FastAPI

from prcp.api.schemas import ServiceCreate

app = FastAPI(title="Platform Reliability Control Plane")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/service")
def create_service(service: ServiceCreate):
    return service.create_service()
