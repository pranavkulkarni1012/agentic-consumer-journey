# Configuration examples

Templates for the organisation-specific settings the tools and engine read. Copy to
`config/<name>.yaml`, fill in real values, and keep them in git (they contain no secrets).
All values here are **placeholders**. Changes are reviewed by CODEOWNERS and run the eval suite.

| File | Used by | Who owns the content |
|---|---|---|
| `scopes.yaml` | Authorisation (docs/07) | Platform + security |
| `group-prefixes.yaml` | ID-03 filter | IAM |
| `attribute-map.yaml` | ID-07, IM-02, EN-01 | IAM + governance |
| `data-mesh-scope.yaml` | SF-04 and all Snowflake tools | Snowflake platform |
| `immuta.yaml` | Immuta connector, SF-02, SF-07 | Immuta admin |
| `rls-models.yaml` | EN-01, DX-03 | Governance + data stewards |
| `pi-classification.yaml` | EN-02, DX-04 | Governance |
| `sync-windows.yaml` | Engine propagation and lag rules | IAM + platform owners |
| `error-catalog.yaml` | WF-02, DX-02 | This team (seed list; extend from real history) |
| `access-request-routes.yaml` | Next actions | IAM + helpdesk |
| `access-contracts/sales-orders.yaml` | DP-02 fallback | Data product owner |

Not included as examples because they are derived during the build:

- `root-causes.yaml`: the root cause catalog from `docs/06-diagnostic-model.md` section 3, with
  message and remediation templates per code (created in story CAA-150).
- `onboarding/`: prerequisite templates and connection profiles (Phase 4, `docs/11`).
