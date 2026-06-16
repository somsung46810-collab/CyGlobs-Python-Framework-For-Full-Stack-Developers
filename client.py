import requests
from framework.protocol import RequestEnvelope, ResponseEnvelope
from framework.contingency import RetryPolicy
from framework.config import ClientConfig


class FrameworkClient:
    def __init__(self, config: ClientConfig | None = None):
        self.config = config or ClientConfig()
        self.retry_policy = RetryPolicy(max_retries=self.config.max_retries)

    def call(self, operation: str, payload: dict | None = None) -> ResponseEnvelope:
        payload = payload or {}

        request = RequestEnvelope(
            operation=operation,
            payload=payload,
        )

        def send_request() -> ResponseEnvelope:
            response = requests.post(
                f"{self.config.base_url}/rpc",
                json=request.model_dump(),
                timeout=self.config.timeout_seconds,
            )
            response.raise_for_status()
            return ResponseEnvelope(**response.json())

        return self.retry_policy.run(send_request)


if __name__ == "__main__":
    client = FrameworkClient()

    print(client.call("health").model_dump())
    print(client.call("echo", {"message": "Hello from CyGlobs client"}).model_dump())
    print(client.call("compare", {"left": 10, "right": 10}).model_dump())
