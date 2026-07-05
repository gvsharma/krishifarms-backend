from dataclasses import dataclass

from fastapi import Header


@dataclass(frozen=True)
class ClientContext:
    device_id: str | None
    client_type: str | None
    request_id: str | None


def get_client_context(
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    x_client_type: str | None = Header(default=None, alias="X-Client-Type"),
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> ClientContext:
    client_type = (x_client_type or "api").strip().lower()[:30] or "api"
    device_id = x_device_id.strip()[:100] if x_device_id else None
    request_id = x_request_id.strip()[:100] if x_request_id else None
    return ClientContext(device_id=device_id, client_type=client_type, request_id=request_id)
