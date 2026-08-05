from fastapi.testclient import TestClient


def test_environment_create_returns_201(client: TestClient) -> None:
    response = client.post(
        url="/environments",
        json={"name": "dev-us-south", "region": "us-south", "cluster": "dev-cluster"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "name": "dev-us-south",
        "region": "us-south",
        "cluster": "dev-cluster",
    }


def test_list_environments_returns_created_environments(client: TestClient) -> None:
    client.post(
        url="/environments",
        json={"name": "dev-us-south", "region": "us-south", "cluster": "dev-cluster"},
    )

    response = client.get("/environments")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "dev-us-south", "region": "us-south", "cluster": "dev-cluster"}
    ]


def test_get_service_by_name_is_success(client: TestClient) -> None:
    client.post(
        url="/environments",
        json={"name": "dev-us-south", "region": "us-south", "cluster": "dev-cluster"},
    )
    response = client.get(url="/environments/dev-us-south")
    assert response.status_code == 200
    assert response.json() == {
        "name": "dev-us-south",
        "region": "us-south",
        "cluster": "dev-cluster",
    }


def test_get_service_by_name_raise_404_if_not_found(client: TestClient) -> None:
    response = client.get("/environments/missing-environment")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Environment not found",
        "instance": "/environments/missing-environment",
        "status": 404,
        "title": "Not Found",
        "type": "urn:prcp:error:http-404",
    }
