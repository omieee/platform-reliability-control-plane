from uuid import UUID


class PRCPError(Exception):
    status: int
    title: str
    error_type: str

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class DuplicateServiceError(PRCPError):
    status = 409
    title = "Service already exists"
    error_type = "urn:prcp:error:service-conflict"

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(f"Service '{service_name}' already exists")


class DuplicateEnvironmentError(PRCPError):
    status = 409
    title = "Environment already exists"
    error_type = "urn:prcp:error:environment-conflict"

    def __init__(self, environment_name: str) -> None:
        self.environment_name = environment_name
        super().__init__(f"Environment '{environment_name}' already exists")


class DuplicateProbeError(PRCPError):
    status = 409
    title = "Probe already exists"
    error_type = "urn:prcp:error:probe-conflict"

    def __init__(self, existing_probe_id: UUID) -> None:
        self.existing_probe_id = existing_probe_id
        super().__init__(f"Probe already exists with ID '{existing_probe_id}'")
