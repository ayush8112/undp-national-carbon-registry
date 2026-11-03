# Roles and permissions layer

## Two axes

- User role (`libs/shared/src/casl/role.enum.ts`): `Root`, `Admin`, `Manager`, `ViewOnly`.
- Company role (`enum/company.role.enum.ts`): `DNA` (Designated National Authority), `PD` (Project Developer), `IC` (Independent Certifier), `Ministry`, `ClimateFund`, `ExecutiveCommittee`, `API`.

Ability = company role plus user role, built in `casl/casl-ability.factory.ts`, enforced by `policy.guard.ts` and the `@Policy()` decorator on controllers. Frontend mirror: `web/src/Casl/ability.ts` with the `Can` component; kept in sync by hand. Ministry is tested as a mirror of DNA in `cross-cutting.spec.ts`.

## Auth

JWT in `libs/shared/src/auth/`, plus an API key strategy for MRV system integration. Endpoints include `/auth/login`, `/auth/login/refresh`, `/auth/forgotPassword`. There is no `/auth/logout` endpoint.

## Onboarding (README)

1. Setup creates one Root user for the setup email.
2. Root creates the DNA entity and its Admin.
3. DNA Admin creates other companies and their Admins.
4. Company Admin adds Admin, Manager, ViewOnly users.
5. New users get a confirmation email with password. With `IS_EMAIL_DISABLED=true` passwords appear in the `national` logs as `Password (temporary)`.

## User management

| Company | New user role | Who may create or manage |
|-|-|-|
| DNA | Root | Only the default system user exists; Root manages all users |
| DNA | Admin, Manager, ViewOnly | Root, DNA Admin |
| Other companies | Admin, Manager, ViewOnly | Root, DNA Admin, that company's Admin |

Users can edit their own account except role and email, and cannot delete themselves.

## Business decisions owned by DNA

ITMO Authorization approve or reject, retirement approvals, Corresponding Adjustment approval, Cooperative Approach transitions. PD has read only access to Cooperative Approaches. DNA sees Corresponding Adjustments and Initial Reports in the sidebar; PD does not (`layout.sider.tsx`).

## When editing

Change backend factory and frontend ability in the same change, add or update the CASL matrix test in `tests/e2e/article6/cross-cutting.spec.ts`, and confirm the sidebar gate if a menu item is affected.
