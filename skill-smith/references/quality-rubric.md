# 12-point quality rubric

Score each criterion from 1 to 5 with evidence. Ready to publish: average ≥ 4.5 and nothing below 4.

| # | Criterion | 5 means |
| --- | --- | --- |
| 1 | Triggering | The description says what and when, with real and implicit triggers and negative boundaries. |
| 2 | Focus | One clearly bounded competence; no "Swiss-army knife". |
| 3 | Concision | Every line adds something the model would not do on its own. |
| 4 | Progressive disclosure | Long material lives in references/ or scripts/ with instructions on when to use it. |
| 5 | Executability | An agent can follow it from start to end without guessing. |
| 6 | Reliability | Fragile steps use scripts, templates or verification loops. |
| 7 | Examples | 2–3 short, realistic input → output examples. |
| 8 | Robustness | Says how to handle missing, ambiguous or malformed input. |
| 9 | Portability | Generic tool names and manual fallbacks when code cannot run. |
| 10 | Security | No secrets; confirmation before destructive or external actions. |
| 11 | Maintainability | Version, author, consistent terms, no relative dates. |
| 12 | Testability | Positive and negative trigger prompts plus verifiable test cases. |

`python -m skillsmith audit` gives heuristic scores from the files. It does not replace running the tests with a real model.
