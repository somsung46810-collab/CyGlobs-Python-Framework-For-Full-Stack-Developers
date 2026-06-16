from dataclasses import dataclass


@dataclass
class ComparatorResult:
    passed: bool
    reason: str


class ProtocolComparator:
    def __init__(self, expected_version: str):
        self.expected_version = expected_version

    def compare_version(self, actual_version: str) -> ComparatorResult:
        if actual_version == self.expected_version:
            return ComparatorResult(True, "Protocol version matched")

        return ComparatorResult(
            False,
            f"Protocol mismatch: expected {self.expected_version}, got {actual_version}",
        )


class PayloadComparator:
    def require_keys(self, payload: dict, required_keys: set[str]) -> ComparatorResult:
        missing = required_keys - set(payload.keys())

        if not missing:
            return ComparatorResult(True, "Payload contains required keys")

        return ComparatorResult(False, f"Missing required keys: {sorted(missing)}")
