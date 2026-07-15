# API Guide

## Base URLs

- Backend API: `/api/v1`
- Health: `/health`
- Readiness: `/ready`
- Metrics: `/metrics`

## Authentication

Bearer access tokens are used for protected endpoints. The frontend attaches the current access token automatically through the shared HTTP client.

## Key endpoints

- `GET /api/v1/executive/overview`
- `GET /api/v1/executive/kpis`
- `GET /api/v1/executive/trends`
- `GET /api/v1/executive/reports`
- `GET /api/v1/executive/forecasts`
- `GET /api/v1/executive/recommendations`
- `GET /api/v1/executive/decisions`

## Error handling

Standard application errors are returned with structured JSON payloads and HTTP status codes. Missing resources return 404 responses and validation failures return 4xx responses.

## Documentation surfaces

- OpenAPI: `/openapi.json`
- Swagger UI: `/docs`
- ReDoc: `/redoc`
