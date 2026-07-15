# Banking Intelligence Architecture

The banking intelligence layer combines transaction intelligence, fraud detection, AML analytics, UEBA, device intelligence, identity risk, and graph-based financial crime analysis into a single explainable platform.

## Core Flow

1. Register and validate transactions.
2. Enrich events with customer, merchant, device, and identity context.
3. Score fraud, AML, behavior, and account risk in real time.
4. Build customer, merchant, account, and fraud profiles.
5. Generate investigation cases and recommendations.
6. Project graph relationships across customers, merchants, accounts, devices, and transactions.
7. Persist operational analytics and expose them through APIs.

## APIs

- `POST /fraud/analyze`
- `POST /fraud/score`
- `POST /fraud/investigate`
- `POST /aml/analyze`
- `POST /transactions/analyze`
- `GET /customers/{id}/risk`
- `GET /merchants/{id}/risk`
- `GET /accounts/{id}/risk`
- `POST /ueba/analyze`
- `GET /risk/dashboard`
- `GET /fraud/cases`
