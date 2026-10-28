# Test suite template

Save as `evals/tests.yaml` next to SKILL.md (or `tests/triggers.json` for the CLI starter).

```yaml
skill_name: weekly-sales-report
positive_triggers:            # 5 or more — must activate
  - prompt: "Can you turn this sheet into the weekly update for the board?"
    expected_action: "ACTIVATED"
  - prompt: "sales status for last week pls"      # informal, with a typo-tolerant phrasing
    expected_action: "ACTIVATED"
negative_triggers:            # 3 or more near misses — must NOT activate
  - prompt: "Audit the balance sheet for Q3."
    expected_action: "NOT_ACTIVATED"
    reason: "Accounting audits belong to ledger-review."
operational_cases:            # 3 or more — observable criteria
  - test_id: "TC-01"
    input: "fixtures/sales_week_41.csv"
    verification_criteria:
      - "Report has the sections Summary, KPIs, Risks."
      - "Revenue total equals the sum of the input rows."
```

Run each prompt in a fresh conversation with the skill installed and record activated / not activated. Compare outputs with and without the skill.
