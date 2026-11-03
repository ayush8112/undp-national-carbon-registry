# Architecture layer

Snapshot of registry v2.0. Verify paths in the repo before relying on them (Step 2 of SKILL.md).

## One NestJS app, many modules

`backend/services/src/main.ts` reads comma separated `RUN_MODULE` (default `national-api`).

| Module | Kind | Mount or role |
|-|-|-|
| `national-api` | HTTP | `/national`. Auth, users, companies, projects, credits, Cooperative Approaches, Initial Reports, Corresponding Adjustments, AEF V2, CAD Trust sync, ITMO accounts, documents, settings. Controllers in `src/national-api/*.controller.ts` |
| `analytics-api` | HTTP | `/stats`. Read only statistics from the operational DB |
| `replicator` | one shot | `src/ledger-replicator/`. Streams ledger events into the operational DB (`process.event.service.ts`) |
| `async-operations-handler` | one shot | Queued work such as email. `ASYNC_OPERATIONS_TYPE=Database\|Queue` |
| `cadtrust-operations-handler` | one shot | CAD Trust lane: own cursor, own loop, recurring reconcile timer. `src/async-operations-handler/cadtrust-async-operations-handler.service.ts` |
| `data-importer` | one shot | `src/data-importer/importers/`: `itmo-system.service.ts`, `certifier-scrape.service.ts`, `annual-report.service.ts`. `DATA_IMPORT_TYPES` |
| `aef-rollover` | one shot | Manual rerun of the AEF V2 start of year rollover. Normal trigger is `AefV2SchedulerService` in process; Lambda equivalent in `serverless.yml` |

`docker-compose.yml` runs modules as separate containers from one image. `serverless.yml` packages them as Lambda functions.

## Shared libraries

- `@app/shared` = `backend/services/libs/shared/src/`. One folder per concern: `project-management`, `programme`, `programme-ledger`, `credit-blocks-management`, `credit-transactions-management`, `serial-number-management`, `cooperative-approach`, `initial-report`, `corresponding-adjustment`, `aef-report-management`, `aef-v2-registry`, `cadt`, `cadtrust-sync`, `itmo-account`, `company`, `user`, `auth`, `casl`, `document-management`, `file-handler`, `location`, `email`, `async-operations`, `audit-logs`, `analytics`, `annualreport`, `registry-client`, `setup`, `validation`, `i18n`. Cross cutting: `entities/`, `view-entities/`, `dto/`, `enum/`, `constants/`, `ledger-db/`.
- `@app/core` = `backend/services/libs/core/src/app-config/` (`configuration.ts` reads all env vars).
- Migrations: `backend/services/src/migrations/`, data source `src/data-source.ts`.

## Dual database

| | Ledger DB | Operational DB |
|-|-|-|
| Role | System of record | Query side |
| Code | `ledger-db/ledger.db.interface.ts`; `pgsql-ledger.service.ts` (default), `qldb-ledger.service.ts` | Postgres, `view-entities/` |
| Selector | `LEDGER_TYPE=PGSQL\|QLDB` | n/a |
| Filled by | national-api writes | replicator, asynchronously, enriched (for example geolocation) |

Consequence: a write is not instantly readable from list endpoints or analytics. Always rule out replicator lag first.

## Pluggable services

| Env var | Values | Interface |
|-|-|-|
| `LOCATION_SERVICE` | `FILE`, `OPENSTREET`, `MAPBOX` | `location/location.interface.ts` |
| `FILE_SERVICE` | `LOCAL`, `S3`, `AZURE` | `file-handler/filehandler.interface.ts` |
| `ASYNC_OPERATIONS_TYPE` | `Database`, `Queue` | async operations |
| `LEDGER_TYPE` | `PGSQL`, `QLDB` | ledger interface |

File storage rule: uploads store a bare key (`documents/foo.pdf`). The global `file-url.interceptor.ts` turns keys into URLs on outbound HTTP via the backend's `getUrl()`. Server side consumers (email attachments, PDF links, exports) must call `resolveStoredFile()`. Anything receiving a reference back from a client must call `toStorageKey()`. Absolute URLs match no prefix and pass through.

Extension rule: new optional behaviour is a new implementation of an interface, selected by env var. Never a hard coded branch.

## Frontend (`web/src`)

| Path | Purpose |
|-|-|
| `Config/apiConfig.ts` | API base URLs and endpoints |
| `Config/uiRoutingConfig.ts` | Route table |
| `Config/colorConfigs.ts` | Theme colours |
| `Definitions/Enums/` | Vocabularies mirroring backend `enum/` |
| `Casl/ability.ts`, `Casl/Can.ts` | UI permission gating |
| `Context/` | User, settings, connection state |
| `Pages/` | One folder per feature, mirroring backend concerns |
| `Components/Sider/layout.sider.tsx` | Sidebar, role gated menu items |
| `locales/`, `public/locales/` | i18next namespaces |

## Commands

Backend from `backend/services/`: `yarn install --frozen-lockfile`, `yarn build`, `yarn start:dev`, `yarn lint`, `yarn test`, `yarn test -- path.spec.ts --testNamePattern "x"`, `yarn test:cov`, `yarn test:e2e` (jest, not Playwright), `yarn migration:generate|create|run|revert|show`.

Frontend from `web/`: `yarn dev` (port 3030), `yarn build`, `yarn lint`, `yarn preview`.
