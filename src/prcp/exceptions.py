class DuplicateServiceException(Exception):
    def __init__(self, service_name: str) -> None:
        super().__init__(f"Service '{service_name}' already exist")
        self.service_name = service_name
