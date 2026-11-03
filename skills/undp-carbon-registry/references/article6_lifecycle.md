# Article 6.2 lifecycle layer

Sources: `docs/business/article6-credit-lifecycle-flow.md`, `libs/shared/src/enum/*.ts`, `README.md` serial section. Decision references used by the repo: 2/CMA.3, 3/CMA.3, 4/CMA.6 Annex II, 6/CMA.4 Annex I and paragraph 17.

## Project lifecycle

`ProjectProposalStage` values: `SUBMITTED_INF`, `APPROVED_INF`, `REJECTED_INF`, `SUBMITTED_COST_QUOTATION`, `SUBMITTED_PROPOSAL`, `SUBMITTED_VALIDATION_AGREEMENT`, `ACCEPTED_PROPOSAL`, `REJECTED_PROPOSAL`, `SUBMITTED_CMA`, `REJECTED_CMA`, `APPROVED_CMA`, `VALIDATION_PENDING`, `REJECTED_VALIDATION`, `AUTHORISED`. Authorization creates the project ID (the serial prefix). Then monitoring and verification lead to issuance.

## Serial numbers

Format follows 6/CMA.4 paragraph 17: `PROJECTID-START-END-VINTAGE`, for example `CA0004-VU-CH-356-1-3000-2023`.

- Each issuance batch continues numbering: batch 2 of 2000 after 3000 is `3001-5000`.
- Full block transfer: owner changes, range unchanged.
- Partial transfer or retirement of N from `S-E`: current owner keeps `S` to `E-N`, counterparty gets `E-N+1` to `E`. Example 1000 from `1-3000`: owner keeps `1-2000`, counterparty gets `2001-3000`.
- Compute with `scripts/serial_number.py`.

## OMGE and SOP deductions at issuance

Config in `libs/core/src/app-config/configuration.ts`: `ITMO_OMGE_PERCENTAGE` (default 2), `ITMO_SOP_PERCENTAGE` (default 5), `ITMO_AUTO_DEDUCT_AT_ISSUANCE` (true unless `"false"`). Organisation level `omgePercentage` also exists.

`omge = floor(total * omge% / 100)`, `sop = floor(total * sop% / 100)`, `net = total - omge - sop`. Deducted amounts route to accounts `CancellationOMGE` and `CancellationSOP`.

## Credit blocks

- Every block starts as **MO** (domestic).
- Transaction types: `Issued`, `Transfered`, `Retired`, `ItmoAuthorized`, `Acquired` (spelling as in code).
- Transaction status: `Pending`, `Completed`, `Rejected`, `Cancelled`.

### Retirement subtypes and who may use them

| Subtype (code value) | MO | ITMO purpose NDC | ITMO purpose OIMP or Other | Triggers CA |
|-|-|-|-|-|
| `Voluntary Cancellations` | yes | yes | yes | no |
| `OMGE Cancellation` | yes | yes | yes | no |
| `Use Towards NDC` (domestic) | yes | no | no | no |
| `First Transfer Towards NDC` | no | yes | no | yes |
| `First Transfer For OIMP` | no | no | yes, needs Authorized Entity recipient | yes |

`Use Towards NDC` (host country, domestic) and `First Transfer Towards NDC` (acquiring Party, international) are opposite ends of the boundary. Do not merge them.

## Cooperative Approach

Status (`cooperative.approach.status.enum.ts`): `Draft`, `Submitted`, `Active`, `Suspended`, `Completed`, `Revoked`.

- Created as Draft with participating Parties and a host.
- Authorized Entities can be attached in Draft or Active.
- Draft to Active only after an Initial Report is submitted.
- Active to Suspended is reversible. Completed and Revoked are terminal. Revoked can never back a new first transfer.
- Only Active can be chosen for ITMO Authorization.

## Initial Report

Status: `Draft`, `Submitted`, `Published`. Implements the Article 6.2 paragraph 18 initial notification. Revisions are kept, not overwritten, while the Cooperative Approach is Draft.

## ITMO Authorization

Preconditions: block is MO; Cooperative Approach is Active.
Chosen at request: amount (partial splits the block, authorized part becomes the new ITMO block), Cooperative Approach, optional purpose.
Purpose enum: `UseTowardsNDC`, `OtherInternationalMitigationPurposes`, `OtherPurposes`. No purpose means NDC.
Decision by DNA: approve (full or partial), reject (stays MO). Requester may cancel while pending.

## Corresponding Adjustment

- Inputs: NDC targets (single year or multi year budget) and national GHG inventory, both migrated in periodically, not entered by users.
- Method enum `ca.method.enum.ts`: `Trajectory`, `Averaging`, `MultiYear`. Business doc describes single year (safeguard check: inventory plus net first transferred ITMOs against the year target) and multi year (indicative annual figure mid period, full reconciliation at the final year).
- Status `ca.status.enum.ts`: `Draft` (recalculable), `Submitted`, `Approved` (by DNA).
- Registry wide reconciliation: all time net first transferred ITMOs against recorded adjustments including Draft, showing any gap.
- Calculated per Cooperative Approach and year.

## Invariants (never break)

1. No international use without ITMO Authorization under an Active Cooperative Approach.
2. No Active Cooperative Approach without a submitted Initial Report.
3. NDC and OIMP first transfers are exclusive by purpose.
4. Use Towards NDC is MO only.
5. First transfer approval is the Corresponding Adjustment trigger; cancellations never are.
6. Partial splits keep the low end with the current owner.
7. An ITMO block cannot be authorized again.
