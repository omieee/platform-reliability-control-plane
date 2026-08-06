from prcp.api.errors import get_http_title


def test_get_http_title_returns_standard_phrase() -> None:
    assert get_http_title(404) == "Not Found"


def test_get_http_title_returns_fallback_for_unknown_status() -> None:
    assert get_http_title(499) == "Custom HTTP Error"
