# Testing layer

## Unit

Jest, `*.spec.ts` under `backend/services/src` and `libs`. Run from `backend/services`: `yarn test`, or one file with `yarn test -- path.spec.ts --testNamePattern "x"`.

## Playwright E2E

- Config `playwright.config.ts` at repo root; specs `tests/e2e/article6/*.spec.ts`: `aef-reporting`, `cooperative-approach`, `corresponding-adjustment`, `credit-issuance`, `credit-transfer`, `cross-cutting`, `initial-report`, `itmo-lifecycle`, `omge-sop-deductions`, `programme-lifecycle`, `retirement`.
- Support: `support/api-client.ts`, `auth.ts`, `fixtures.ts` (role clients such as `apiDna`, `apiPd`), `factories.ts` (`createProgramme`, `authorizeProgramme`, `issueCredits`, `initiateTransfer`, `performRetireAction`, `seed*Direct` helpers).
- No root `package.json`: install `@playwright/test` ad hoc, then `npx playwright test`.
- Needs the live stack: API `http://localhost:3000`, web `http://localhost:3030`.
- `seed*Direct` factories run `podman exec db psql`; override container with `E2E_DB_CONTAINER`. Use podman-compose.
- Coverage matrix and gaps: `docs/testing/e2e-coverage.md`. Update it when coverage changes.

## Replicator lag

Reads lag writes. Before treating an E2E failure as a regression, confirm the `replicator` container is up; earlier "pre existing failures" passed once it was restarted. New tests should poll, or seed the operational DB directly with a `seed*Direct` factory.

## Manual QA and demo data

- `docs/testing/manual-qa-article6.md`: walkthrough, wipe and reseed procedure, seeded data reference.
- `docs/testing/article6-walkthrough-with-screenshots.md`.
- `scripts/seed-demo.sh` needs the stack, `python3`, `curl`.

## Test conventions

- Name new direct seed helpers `seed<Thing>Direct`.
- Every new CASL rule gets a case in the cross-cutting matrix.
- Edge case tests assert a specific error code, guard or formula value, not only status 200.
