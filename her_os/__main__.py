from __future__ import annotations

import json

from .runtime import HerRuntime, Request, TransformDirective


def main() -> None:
    runtime = HerRuntime()
    print("Her VM prototype — commands: request, inject, state, quit")
    while True:
        try:
            line = input("her> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in {"quit", "exit"}:
            break
        try:
            command, _, data = line.partition(" ")
            payload = json.loads(data or "{}")
            if command == "request":
                result = runtime.request(
                    Request(
                        package=str(payload.get("package", "unknown")),
                        updates=tuple(payload.get("updates", [])),
                        payload=dict(payload.get("payload", {})),
                    )
                )
            elif command == "inject":
                directive = TransformDirective(payload["directive"])
                result = runtime.inject(directive, dict(payload.get("payload", {})))
            elif command == "state":
                result = {
                    "stack": runtime.STACK_ID,
                    "tick": runtime.vector.tick,
                    "restraint": runtime.vector.restraint,
                    "buckets": len(runtime.pool.snapshot()),
                }
            else:
                raise ValueError(f"unknown command: {command}")
            print(json.dumps(result, indent=2))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
