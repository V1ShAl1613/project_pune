from __future__ import annotations


def test_identity_routes_are_registered(app) -> None:
    route_paths = {getattr(route, "path", None) for route in app.routes}

    assert "/identity/tenants" in route_paths
    assert "/identity/users" in route_paths
    assert "/identity/directory/search" in route_paths
