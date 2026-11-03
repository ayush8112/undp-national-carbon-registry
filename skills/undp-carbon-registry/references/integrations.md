# Integrations and reporting layer

## AEF V2 (Agreed Electronic Format, 4/CMA.6 Annex II)

Full mapping: `docs/business/aef-v2-field-mappings.md`. Filed with CARP (Common Analysis and Reporting Platform).

- Five tables: Submission, Authorizations, Actions, Holdings, Authorized entities.
- Field labels: `NA` (literal text written, rendered grey italic), "Populated by CARP" (left blank), "registry extension" (local sectors or scopes routed to an added Other option, pending CARP confirmation).
- Action types (`aef.action.type.enum.ts`): `authorization`, `firstTransfer`, `transfer`, `acquisition`, `retire`, `crossBoarderTransfer` (spelling as in code), `useTowardsNDC`, `useForOIMP`, `voluntaryCancellation`, `omgeCancellation`, `holdingsSnapshot`.
- Code: `libs/shared/src/aef-report-management/`, `aef-v2-registry/`, controller `aef-v2.controller.ts`, scheduler `aef-v2.scheduler.ts`, rollover module `src/aef-rollover/`.
- Controlled vocabulary source: "List of common nomenclatures under Article 6, paragraph 2" (17 February 2026), as named in the repo doc.

## CAD Trust V2 sync

Full scope: `docs/business/cadtrust-v2-sync.md`. Separate from the older V1 integration.

- Records are staged privately on the registry's CAD Trust node, then published in a commit batch. Never written directly to the network.
- Updates are full replacement of the project or unit record, re derived from current registry state.
- Configurable values are per deployment; do not state defaults.
- "Not synced" items are deliberate scope decisions, listed in the doc's Section 6.
- Code: `libs/shared/src/cadt/`, `cadtrust-sync/`, controller `cadtrust-sync.controller.ts`, module `cadtrust-operations-handler`, enums `cadtrust.*.enum.ts`.

## UNDP ITMO Voluntary Bilateral Cooperation Platform

README section "External Connectivity". `data-importer` with `itmo-system.service.ts`: daily pull of authorized projects, push of issuances. Field mapping and ITMO sector mapping tables live in the README; read them before editing the importer.

## Other importers

`certifier-scrape.service.ts`, `annual-report.service.ts`, selected through `DATA_IMPORT_TYPES`. Add a new importer by implementing `src/data-importer/importer.interface.ts`.

## Rules

- A report or sync field must be derived from registry state; if no source exists it is `NA` or "Populated by CARP", never a guessed value.
- Changing a mapping means updating the business doc in the same change.
