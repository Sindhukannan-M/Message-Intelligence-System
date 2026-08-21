from enum import Enum


class Route(str, Enum):
    LOCAL = "process_locally"
    CONFIRM = "ask_for_confirmation"
    BLOCK = "blocked"


def route_request(
    *,
    contains_sensitive_data: bool = False,
    sensitivity_type: str | None = None,
    external_service_requested: bool = False,
    high_risk: bool = False,
) -> dict:
    """
    Decide how a request should be handled based on privacy risk.

    The routing decision is conservative:
    - Safe requests stay local.
    - Sensitive data requires confirmation before external processing.
    - High-risk sensitive requests are blocked.
    """

    signals = []

    if contains_sensitive_data:
        signals.append("sensitive_information")

    if sensitivity_type:
        signals.append(sensitivity_type)

    if external_service_requested:
        signals.append("external_service_requested")

    if high_risk:
        signals.append("high_risk")

    if high_risk and contains_sensitive_data:
        route = Route.BLOCK
        reason = (
            "The request contains high-risk sensitive information "
            "and should not be sent to an external service."
        )

    elif contains_sensitive_data and external_service_requested:
        route = Route.CONFIRM
        reason = (
            "Sensitive information was detected and external "
            "processing was requested, so confirmation is required."
        )

    else:
        route = Route.LOCAL
        reason = (
            "No condition requiring external processing or "
            "additional privacy confirmation was detected."
        )

    return {
        "route": route.value,
        "signals": signals,
        "reason": reason,
    }