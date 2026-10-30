# Class Relationships

In this section we will understand some of class structures used in this project

# Aggregation
Following is one exampel where we have used aggregation between twoc classes 
see probe takes environment and service but those are created seprately and a refrence is passed like a probe "has a" environment / service and if probe goes away stil environment and service will exist it is an agregation

# Composition

We don't have a pure composition where completly we can say one of our class compltly "owns" another class . The closest to that would be `id=uuid4(),` in `crete_http+probe` function.

# Association
`expected_status_code: HTTPStatus = HTTPStatus.OK,` we see this at multiple places it is used straight forward the value of OK gets stored at default

# Tightly Coupled

The probe post endpoint is tightly couple with crwting http probe only going forward it should be able to create many more probes:

```
 probe = create_http_probe(
        environment=environment,
        service=service,
        method=request.method,
        path=request.path,
        expected_status_code=request.expected_status_code,
        timeout_seconds=request.timeout_seconds,
    )

    probe_repository.save(probe)
```
