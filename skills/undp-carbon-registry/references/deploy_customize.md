# Deploy and customize layer

## Containers

`docker-compose up -d --build` (docs assume `podman-compose`). Services: `db`, `national` (`:3000/national`), `stats` (`:3100/stats`), `replicator`, `web` (`:3030`). Env files at repo root: `.env.db`, `.env.national`, `.env.replicator` (copy from `.env.*.example`); full backend reference `backend/services/.env.example`. `docker-compose-image.yml` uses prebuilt images.

## Local without containers

```
cd backend/services
yarn sls:install
serverless invoke local --stage=local --function setup --data '{"rootEmail":"...","systemCountryCode":"..","name":"...","logoBase64":"..."}'
sls offline --stage=local
```
Swagger at `http://localhost:3000/local/national`.

## AWS

`serverless.yml` packages modules as Lambda. See README "Deploy System on the AWS Cloud" and `deployment/`.

## Key env vars

`RUN_MODULE`, `LEDGER_TYPE`, `LOCATION_SERVICE`, `FILE_SERVICE`, `ASYNC_OPERATIONS_TYPE`, `DATA_IMPORT_TYPES`, `IS_EMAIL_DISABLED`, `ITMO_OMGE_PERCENTAGE`, `ITMO_SOP_PERCENTAGE`, `ITMO_AUTO_DEDUCT_AT_ISSUANCE`, `E2E_DB_CONTAINER`. Read `libs/core/src/app-config/configuration.ts` for the full list and defaults.

## Country customization (override, never fork)

| Area | Location |
|-|-|
| Branding and config | `web/src/Config/`, `web/src/Styles/`, `web/public/` |
| Frontend vocabularies | `web/src/Definitions/Enums/` |
| Backend enums and constants | `libs/shared/src/enum/`, `libs/shared/src/constants/` |
| API contracts | `libs/shared/src/dto/` |
| Reference data | `backend/services/countries.json`, `regions.csv`, `organisations.csv`, `users.csv` |
| Module and backend selection | env vars above |
| Translations | `web/public/locales/` (English complete, French and Spanish partial) |

## National implementation

`TOR National Implementation.md` is a sample Terms of Reference: installation, scope (UI design, QA with SMEs, containerized web app, DevOps, analytics, accessibility, handover and training, support with an SLA table), deliverables, required skills. Use it when asked how a country procures or plans a rollout.

## Version notes (`CHANGES.md`)

- 2024-03: "Programmes" renamed "Project"; project creation API payload expanded.
- 2025-03: `carbon-services-lib` merged into this repo; serial number format changed for token level tracking; Node 16 to 20; Craco to Vite; financial and activity modules removed.
