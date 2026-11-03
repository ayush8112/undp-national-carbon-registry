---
name: undp-carbon-registry
description: Expert guide to the UNDP National Carbon Credit Registry v2.0 (Article 6 of the Paris Agreement). Use when working on, explaining, reviewing, debugging, deploying, or customizing this registry: its NestJS backend (national-api, analytics-api, replicator, async-operations-handler, data-importer), React/Vite frontend, dual ledger/operational database design, CASL roles, credit serial numbers, block splitting, ITMO platform sync, or Playwright E2E tests. Works in Claude Code (with the repo), Cowork, and chat (from knowledge only).
---

# UNDP National Carbon Credit Registry

Open source toolkit for tracking, issuing, transferring and retiring carbon credits under Article 6. One NestJS codebase (`backend/services`) runs several logical services; a React/Vite app (`web`) is the frontend.

## How to use this skill by surface

- **Claude Code (repo present):** verify every claim against the files before acting. Read files with explicit offset and limit. Run the commands below from the stated directory.
- **Cowork (files or folder shared):** same as Code if the repo is attached; otherwise ask the user to share the relevant files rather than guessing paths or code.
- **Chat (no repo):** answer from the architecture in this skill. Say clearly when something must be checked in the actual code, and give the file path where it lives.

## Commands

Backend, from `backend/services/`:

| Task | Command |
|---|---|
| Install | `yarn install --frozen-lockfile` |
| Build | `yarn build` |
| Dev (one module) | `yarn start:dev` with `RUN_MODULE` set |
| Lint | `yarn lint` |
| Unit tests | `yarn test` or `yarn test -- path/file.spec.ts --testNamePattern "name"` |
| Coverage | `yarn test:cov` |
| Jest e2e (not Playwright) | `yarn test:e2e` |
| Migrations | `yarn migration:generate <path>`, `migration:create`, `migration:run`, `migration:revert`, `migration:show` (uses `src/data-source.ts`) |
| Serverless offline | `yarn sls:install`, then `sls offline --stage=local` (Swagger at `http://localhost:3000/local/national`) |

Frontend, from `web/`: `yarn dev` (port 3030), `yarn build` (`tsc -b && vite build`), `yarn lint`, `yarn preview`.

Full stack: `docker-compose up -d --build` (docs assume `podman-compose`). Services: `db`, `national` (`:3000/national`), `stats` (`:3100/stats`), `replicator`, `web` (`:3030`). Env from `.env.db`, `.env.national`, `.env.replicator` (see `.env.*.example`) and `backend/services/.env.example`. Emails are off by default (`IS_EMAIL_DISABLED=true`); generated passwords, including root, appear in the `national` logs under `Password (temporary)`.

Demo data: `scripts/seed-demo.sh` (needs the stack, `python3`, `curl`). Reset steps: `docs/testing/manual-qa-article6.md`.

## Playwright E2E

Config `playwright.config.ts` at repo root runs `tests/e2e/article6/**/*.spec.ts`. There is no root `package.json`: install `@playwright/test` ad hoc, then `npx playwright test`. Tests need the live stack. Seed helpers in `tests/e2e/article6/support/factories.ts` call `podman exec db psql` (override with `E2E_DB_CONTAINER`), so run under podman. Coverage and known gaps: `docs/testing/e2e-coverage.md`.

## Architecture

### Modules selected by `RUN_MODULE` (comma separated, default `national-api`)

- `national-api`: `/national`; auth, users, companies, project and credit lifecycle. Controllers in `src/national-api/*.controller.ts`.
- `analytics-api`: `/stats`; read only statistics.
- `replicator`: streams ledger events into the operational DB (`ledger-replicator/process.event.service.ts`).
- `async-operations-handler`: queued work such as email; `ASYNC_OPERATIONS_TYPE=Database|Queue`.
- `data-importer`: external imports such as ITMO sync; `DATA_IMPORT_TYPES`.

`docker-compose.yml` runs each as its own container from one image; `serverless.yml` packages them as Lambda functions.

Shared code: `@app/shared` (`libs/shared/src/`, nearly all domain logic, one folder per concern plus `entities/`, `view-entities/`, `dto/`, `enum/`, `ledger-db/`) and `@app/core` (`libs/core/src/app-config/`).

### Dual database

- **Ledger DB** (system of record) behind `ledger-db/ledger.db.interface.ts`: `pgsql-ledger.service.ts` (default) or `qldb-ledger.service.ts`; `LEDGER_TYPE=PGSQL|QLDB`. A new backend implements this interface.
- **Operational DB** (Postgres read side), filled asynchronously by the replicator and enriched (for example geolocation). Analytics and most list endpoints read it through `view-entities/`.
- Reads lag writes. A freshly written entity may not appear yet; E2E tests poll or seed the operational DB directly. Check the replicator is running before calling a missing record a bug.

### Credit identity

Project ID per project; each issuance gets a serial range aligned with UNFCCC Decision 6/CMA.4 paragraph 17, for example `CA0004-VU-CH-356-1-3000-2023`. A partial transfer or retirement splits the block: the original owner keeps the low end, the counterparty gets a new block for the high end. See `serial-number-management/` and `credit-blocks-management/`.

### Pluggable services (env selected, interface backed)

- `LOCATION_SERVICE=FILE|OPENSTREET|MAPBOX`: `location/location.interface.ts`
- `FILE_SERVICE=LOCAL|S3|AZURE`: `file-handler/filehandler.interface.ts`. Uploads store a bare key (`documents/foo.pdf`); `file-url.interceptor.ts` turns keys into URLs on HTTP responses via `getUrl()`. Server side consumers (email attachments, PDFs, exports) must call `resolveStoredFile()`. Anything taking a reference back from a client must call `toStorageKey()`. Existing absolute URLs pass through unchanged.
- `ASYNC_OPERATIONS_TYPE=Database|Queue`

Rule: add optional features as a new interface implementation selected by env var, never as a hard coded branch in an existing service.

### Authorization

CASL on both sides, kept in sync by hand:
- Backend: `casl/casl-ability.factory.ts`, roles in `role.enum.ts` (Root, DNA, Project Developer, Independent Certifier; each Admin, Manager or ViewOnly), enforced by `policy.guard.ts` and `@Policy()`.
- Frontend: `web/src/Casl/ability.ts` and `Can.ts`.
- JWT auth in `libs/shared/src/auth/`, plus an API key strategy for MRV system integration.

When changing a permission, update both files and say so.

### Frontend (`web/src`)

`Config/apiConfig.ts` (endpoints), `Config/uiRoutingConfig.ts` (routes), `Config/colorConfigs.ts` (branding); `Definitions/Enums` (mirrors backend `enum/`); `Context/` (user, settings, connection); `Pages/` (one folder per feature, mirroring backend modules); `locales/` and `public/locales/` (i18next; English complete, French and Spanish partial).

## Country customization (override, do not fork)

| Area | Location |
|---|---|
| Branding and config | `web/src/Config/`, `web/src/Styles/`, `web/public/` |
| Frontend vocabularies | `web/src/Definitions/Enums/` |
| Backend enums and constants | `libs/shared/src/enum/`, `constants/` |
| API contracts | `libs/shared/src/dto/` |
| Reference data | `backend/services/countries.json`, `regions.csv`, `organisations.csv`, `users.csv` |
| Backend selection | `RUN_MODULE`, `LEDGER_TYPE`, `LOCATION_SERVICE`, `FILE_SERVICE`, `ASYNC_OPERATIONS_TYPE` |
| Translations | `web/public/locales/` |

## ITMO platform integration

`data-importer` pulls authorized projects daily from UNDP's ITMO Voluntary Bilateral Cooperation Platform and pushes issuances. Field and sector mappings are in the root `README.md` under "External Connectivity"; read them before editing `data-importer/importers/`.

## Working checklist

1. Locate the bounded concern in `libs/shared/src/` before touching a controller.
2. Entity change: update entity, DTO, view entity, then generate a migration.
3. Permission change: edit backend factory and frontend ability together.
4. Enum change: keep backend `enum/` and `web/src/Definitions/Enums` parallel.
5. Read side bug: rule out replicator lag first.
6. File references: `toStorageKey()` inbound, `resolveStoredFile()` for server side output.
7. Before finishing: `yarn lint`, `yarn build`, relevant `yarn test` in each touched package.
