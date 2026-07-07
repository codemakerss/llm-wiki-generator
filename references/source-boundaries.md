# Source Boundaries

- `business_fact`
  - may create `source`, `concept`, `entity`, `synthesis`
  - may be written as `stable` when evidence is strong and no conflict is detected

- `industry_practice`
  - may create `source`, `synthesis`, `prd_pattern`
  - must not be treated as customer truth or business rule

- `team_history`
  - may create `source`, `synthesis`, `concept`, `prd_pattern`
  - defaults to `draft`
  - should be treated as historical reference until re-confirmed
  - `prd_pattern` may be extracted from historical PRDs, team decisions, requirement structures, review flows, reusable templates, and repeated product judgments

- `feedback`
  - defaults to `draft`
  - should not become stable automatically

- `conflict`
  - does not overwrite existing pages
  - should be stored under `20-wiki/conflicts/`
