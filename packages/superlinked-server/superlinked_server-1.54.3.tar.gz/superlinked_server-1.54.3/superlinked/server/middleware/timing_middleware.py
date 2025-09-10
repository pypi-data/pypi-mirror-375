# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import structlog
from asgi_correlation_id.context import correlation_id
from beartype.typing import cast
from fastapi import APIRouter
from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from uvicorn._types import HTTPScope
from uvicorn.protocols.utils import get_path_with_query_string

from superlinked.framework.common.telemetry.telemetry_registry import telemetry

access_logger = structlog.stdlib.get_logger("api.access")


class AccessTimingASGIMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.known_routes: set[str] = set()

    def _find_app_instance(self, app: ASGIApp, max_depth: int = 10) -> APIRouter | None:
        """
        Recursively find the APIRouter app instance from the ASGI app stack.
        This is needed because middleware can wrap the app multiple times.
        """
        if max_depth <= 0:
            return None

        if hasattr(app, "app"):
            inner_app = getattr(app, "app")
            if isinstance(inner_app, (APIRouter,)):
                return inner_app
            return self._find_app_instance(inner_app, max_depth - 1)
        return None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if not self.known_routes:
            if fast_api_app := self._find_app_instance(self.app):
                self.known_routes = {route.path for route in fast_api_app.routes if isinstance(route, Route)}

        structlog.contextvars.clear_contextvars()
        request_id = correlation_id.get()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        method = scope.get("method", "GET")
        http_version = scope.get("http_version", "1.1")
        client = cast(tuple[str, int] | None, scope.get("client"))
        client_host = client[0] if client else "no-client"
        client_port = client[1] if client else "no-client"

        start_time = time.perf_counter_ns()
        status_code_holder: dict[str, int | None] = {"status": None}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                status = message["status"]
                status_code_holder["status"] = status

                process_time = time.perf_counter_ns() - start_time
                duration_ms = process_time / 1_000_000  # ns -> ms

                path_qs = get_path_with_query_string(cast(HTTPScope, scope))
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", str(process_time / 10**9).encode("ascii")))
                message["headers"] = headers
                access_logger.debug(
                    "%s",
                    path_qs,
                    status_code=status,
                    method=method,
                    request_id=request_id,
                    version=http_version,
                    client_ip=client_host,
                    client_port=client_port,
                    duration=f"{duration_ms:.2f} ms",
                )

                # TODO: FAB-3723 - Until WAF (INF-540) is in place, we only record metrics for known routes
                if scope.get("path") in self.known_routes:
                    labels = {
                        "path": scope.get("path", ""),
                        "method": method,
                        "status_code": str(status),
                    }
                    telemetry.record_metric("http_requests_total", 1, labels)
                    telemetry.record_metric("http_request_duration_ms", duration_ms, labels)

            await send(message)

        await self.app(scope, receive, send_wrapper)
