from src.privacy_router import route_request


def test_safe_request_is_local():
    result = route_request()

    assert result["route"] == "process_locally"


def test_sensitive_external_request_requires_confirmation():
    result = route_request(
        contains_sensitive_data=True,
        sensitivity_type="personal_information",
        external_service_requested=True,
    )

    assert result["route"] == "ask_for_confirmation"


def test_high_risk_sensitive_request_is_blocked():
    result = route_request(
        contains_sensitive_data=True,
        sensitivity_type="authentication_token",
        external_service_requested=True,
        high_risk=True,
    )

    assert result["route"] == "blocked"