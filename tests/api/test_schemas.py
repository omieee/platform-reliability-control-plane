from fastapi.testclient import TestClient


def test_environment_name_empty_raise_value_error(client: TestClient) -> None:
    response = client.post(
        url="/environments",
        json={"name": "  ", "region": "us-south", "cluster": "dev-cluster"},
    )
    assert response.status_code == 422
