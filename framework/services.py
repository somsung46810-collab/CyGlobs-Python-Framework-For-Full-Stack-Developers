def echo_service(payload: dict) -> dict:
    return {
        "echo": payload.get("message", ""),
        "received": True,
    }


def compare_service(payload: dict) -> dict:
    left = payload.get("left")
    right = payload.get("right")

    return {
        "left": left,
        "right": right,
        "equal": left == right,
        "inverse_equal": left != right,
    }


def health_service(payload: dict) -> dict:
    return {
        "service": "cyglobs-python-client-server-framework",
        "healthy": True,
        "methodology": [
            "comparators",
            "inverse operators",
            "contingency planning",
            "level of indirection",
            "best practices",
        ],
    }
