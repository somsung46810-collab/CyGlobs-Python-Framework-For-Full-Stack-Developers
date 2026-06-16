import logging
from fastapi import FastAPI
from framework.protocol import RequestEnvelope, ResponseEnvelope
from framework.comparators import ProtocolComparator
from framework.inverse_ops import InverseOperatorRegistry
from framework.contingency import FallbackPlanner
from framework.config import ServerConfig
from framework.services import echo_service, compare_service, health_service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

config = ServerConfig()
app = FastAPI(title="CyGlobs Python Client Server Framework")

protocol_comparator = ProtocolComparator(config.protocol_version)
fallback_planner = FallbackPlanner()
operators = InverseOperatorRegistry()

operators.register("echo", echo_service)
operators.register("compare", compare_service)
operators.register("health", health_service)


@app.get("/")
def root() -> dict:
    return {"message": "CyGlobs Python Client Server Framework is running"}


@app.post("/rpc", response_model=ResponseEnvelope)
def rpc(request: RequestEnvelope) -> ResponseEnvelope:
    try:
        comparison = protocol_comparator.compare_version(request.protocol_version)

        if not comparison.passed:
            return ResponseEnvelope(
                protocol_version=config.protocol_version,
                status="error",
                error=comparison.reason,
            )

        result = operators.execute(request.operation, request.payload)

        return ResponseEnvelope(
            protocol_version=config.protocol_version,
            status="ok",
            result=result,
        )

    except Exception as error:
        logger.exception("RPC failure")
        fallback = fallback_planner.fallback_response(error)

        return ResponseEnvelope(
            protocol_version=config.protocol_version,
            status=fallback["status"],
            result=fallback["result"],
            error=fallback["error"],
        )
