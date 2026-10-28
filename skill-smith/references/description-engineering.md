# Description engineering

The description is a natural-language classifier. A vague one never triggers; a broad one collides with other skills.

## Formula
1. **Action verb + result** — "Creates weekly executive sales reports with KPIs and risks…"
2. **Explicit triggers and synonyms** — the words users really type, in every language of the audience ("weekly update", "sales status", "relatório semanal").
3. **Implicit triggers** — "…even if they do not say 'report'".
4. **Negative boundaries** — "Do not use for accounting audits; use ledger-review instead."
5. **Assertive tone** — "Use whenever…" counters the models' tendency to under-trigger.

## Before and after
| Quality | Description | Diagnosis |
| --- | --- | --- |
| Vague | Helps with reports and data. | No input, output, triggers or limits — almost never used. |
| Partial | Formats weekly sales data into PDF files. | Says what, not when; no synonyms or boundaries. |
| Strong | Creates weekly executive sales reports featuring KPIs and risk analysis from spreadsheets. Use whenever the user asks for a weekly update, sales status or revenue summary, even if they do not say "report". Do not use for accounting or balance sheet audits. | What + when + implicit trigger + boundary. |

## Checks
- At most 1024 characters, no `<` or `>`.
- Third person or imperative, no first person.
- Mentions the input type and the output.
- Shares no trigger words with sibling skills unless a boundary separates them.
