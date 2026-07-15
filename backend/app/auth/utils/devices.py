from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RequestDeviceMetadata:
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None
    device_name: str | None = None
    device_fingerprint: str | None = None
    geo_location: dict[str, object] | None = None


def build_device_metadata(
    *,
    ip_address: str | None,
    user_agent: str | None,
    device_id: str | None,
    device_name: str | None,
    device_fingerprint: str | None,
) -> RequestDeviceMetadata:
    return RequestDeviceMetadata(
        ip_address=ip_address,
        user_agent=user_agent,
        device_id=device_id,
        device_name=device_name,
        device_fingerprint=device_fingerprint,
        geo_location={"country": None, "region": None, "city": None},
    )
