---
name: undp-carbon-registry
description: Orchestrator for the UNDP National Carbon Credit Registry v2.0 (Article 6.2 of the Paris Agreement). Use for any task about this registry, in Claude Code, Cowork or chat: explaining its business rules (MO and ITMO blocks, Cooperative Approaches, Initial Reports, first transfers, Corresponding Adjustments, OMGE and SOP deductions), developing or debugging its NestJS backend or React frontend, CASL roles, ledger and replicator behaviour, serial numbers and block splits, AEF V2 reporting, CAD Trust V2 sync, the UNDP ITMO platform importer, Playwright E2E tests, deployment, or per-country customization. Do not use for general carbon market or Article 6 policy questions with no link to this codebase, or for citing papers and standards (research-analyst owns citation verification).
---

# UNDP Carbon Registry Skill

This skill is an orchestrator. It decides which layer of the registry a request touches, loads only the reference file for that layer, and checks every claim against the real code before it reaches the answer. It adds four things a plain reading of the repo does not: a surface check (Code, Cowork or chat), a source of truth gate, fixed loading rules for the reference files, and two scripts for checks that must be exact (serial number arithmetic and backend/frontend enum drift).

## Precedence with other skills and agents

| Situation | Leading skill or agent | What this skill owns |
|-|-|-|
| Code change inside `backend/services` | `backend-engineer` agent if present, else this skill | Business rules (Step 4), checklist (Step 6) |
| Code change inside `web/` | `frontend-engineer` agent if present, else this skill | CASL mirror and enum mirror checks |
| Playwright suite, seed scripts, testing docs | `e2e-qa-engineer` agent if present, else this skill | Replicator lag rule, factory conventions |
| Commit, lint, typecheck, migrations | repo commands `commit`, `lint-fix`, `typecheck`, `migration` | Nothing beyond Step 6 |
| Answer cites Paris Agreement decisions, papers or standards with identifiers | research-analyst | Mapping the decision to registry behaviour |
| General Article 6 policy, no registry link | other skills | Nothing, do not load this skill |

## Surface check, read before Step 1

1. **Claude Code with the repo:** the repo is the source of truth. Find it by the presence of `backend/services/src/main.ts` and `web/src/Casl/ability.ts`. Run `python3 scripts/registry_probe.py ROOT` once per conversation; it reports modules, enum drift and which docs exist. Read files with explicit offset and limit.
2. **Cowork:** if the folder is shared, treat it as Claude Code. If only some files are shared, ask for the specific file named in the reference before asserting anything about its contents.
3. **Chat:** answer from the reference files. Mark any statement about current code as "per the v2.0 snapshot in this skill" and give the file path the user should check. Never invent a function, endpoint or field name that is not in the references.
4. `scripts/serial_number.py` needs only Python, so it works in every surface that can run code. Where code cannot run, do the arithmetic by hand using the rule in `references/article6_lifecycle.md` and show the working.

## Loading the reference files

Load by fixed rule, not by feel. Load only the file for the layer touched; load a second only when the task crosses layers.

| File | Load when |
|-|-|
| `references/architecture.md` | Any backend change, any question about modules, ledger, replicator, file storage, location, async work |
| `references/article6_lifecycle.md` | Any question or change touching credit blocks, statuses, transfers, retirements, authorization, Cooperative Approaches, Initial Reports, Corresponding Adjustments, OMGE or SOP |
| `references/roles_permissions.md` | Any permission, role, onboarding or "who can do X" question; any CASL edit |
| `references/integrations.md` | AEF V2 reports, CAD Trust V2 sync, ITMO platform importer, certifier scrape, annual report import, AEF rollover |
| `references/testing.md` | Writing or fixing tests, flaky tests, seeding, manual QA |
| `references/deploy_customize.md` | Running the stack, env vars, AWS or container deployment, branding, localization, country rollout, TOR questions |

Do not load all six for a single fact. A one line question ("what does SOP mean here") needs only its file.

## Step 1: Classify the request

| Mode | Signal | What runs |
|-|-|-|
| Explain | "how does", "why can't", "what is", business flow, onboarding | Step 4, answer in business terms first, code paths second |
| Develop | add, change, implement, migrate | Steps 2 to 6 |
| Debug | error, wrong value, missing record, flaky | Step 5 first, then Steps 2 to 6 |
| Integrate or report | AEF, CAD Trust, ITMO, export | `integrations.md`, then Step 4 |
| Operate | run, deploy, configure, customize, translate | `deploy_customize.md` |

Ask one clarifying question only when the mode changes which layer is touched.

## Step 2: Source of truth gate

Before stating or relying on any rule, confirm where it lives. Order of authority:

1. Code (`libs/shared/src/**`, controllers, `web/src/**`)
2. Repo business docs (`docs/business/*.md`)
3. Testing docs (`docs/testing/*.md`)
4. `README.md`, `CHANGES.md`, `CLAUDE.md`
5. This skill's references

If a lower source disagrees with a higher one, the higher one wins and the answer says so. Known example: the business doc speaks of "single year" and "multi year" Corresponding Adjustment methods, while the enum `ca.method.enum.ts` holds `Trajectory`, `Averaging`, `MultiYear`. Report the enum values when talking about code.

## Step 3: Locate the layer

Use the layer map in `references/architecture.md`. Find the bounded concern folder in `libs/shared/src/` before touching any controller; controllers in `src/national-api/` are thin.

## Step 4: Apply the business rules

Every change or explanation touching credits must respect the invariants in `references/article6_lifecycle.md`. The short list, which must never be broken:

- An MO can only go international after ITMO Authorization under an Active Cooperative Approach.
- A Cooperative Approach becomes Active only after its Initial Report is submitted.
- First Transfer Towards NDC needs purpose NDC; First Transfer For OIMP needs purpose OIMP or Other and a named Authorized Entity. They are mutually exclusive.
- Use Towards NDC is MO only. Voluntary and OMGE Cancellation are open to MO and ITMO of any purpose.
- Approval of a first transfer is the event that creates the Corresponding Adjustment obligation.
- Partial splits: the current owner keeps the low end of the serial range.

## Step 5: Debug protocol

1. Read side missing or stale: check the `replicator` is running and caught up before calling it a bug. Reads come from the operational DB, writes go to the ledger.
2. File link broken: check whether the value is a bare storage key or an absolute URL, and whether a server side path skipped `resolveStoredFile()`.
3. Permission denied unexpectedly: compare `casl-ability.factory.ts` with `web/src/Casl/ability.ts`; drift is the usual cause.
4. Dropdown or status mismatch between UI and API: run `scripts/registry_probe.py ROOT --drift`. Some drift is intentional (the frontend company role list is a wider UI vocabulary); a missing status value such as `Revoked` in the frontend Cooperative Approach enum is a real gap. Judge each row, do not auto fix.
5. Serial range looks wrong after a transfer: recompute with `scripts/serial_number.py split`.
6. E2E flake: see `references/testing.md`, replicator lag section, before touching the test.

## Step 6: Finish checklist (Develop and Debug)

1. Entity change: entity, DTO, view entity, migration (`yarn migration:generate`).
2. Permission change: backend factory and frontend ability edited together.
3. Enum change: backend `libs/shared/src/enum/` and `web/src/Definitions/Enums/` kept parallel; rerun drift check.
4. New optional backend: new interface implementation selected by env var, never a hard coded branch.
5. File references: `toStorageKey()` inbound, `resolveStoredFile()` for server side output.
6. Run `yarn lint`, `yarn build`, relevant `yarn test` in each touched package; for Article 6 flows, the matching Playwright spec.
7. Update `docs/testing/e2e-coverage.md` if test coverage changed, and the business doc if a rule changed.

## Script self checks

After editing a script run `python3 scripts/serial_number.py --selftest` (11 checks: parse, split, next batch, OMGE and SOP rounding, bad input). `registry_probe.py` is read only and exits 1 outside a registry checkout.

## Error handling

- Reference says one thing, code another: trust code, tell the user, suggest updating the reference.
- File named in a reference is missing: say so, search for its new location by concern name, never guess its contents.
- Script cannot run: do the check by hand and label it "manual".
- Unsure whether a rule is business policy or implementation detail: say which source it came from.
