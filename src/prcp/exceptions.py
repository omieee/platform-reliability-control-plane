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
