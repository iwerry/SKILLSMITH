# Agents, multi-agent teams and harnesses

## Agent (persona)
A system prompt with four sections — **Role**, **How you work**, **Deliver**, **Avoid** — plus suggested starters, the skills it may load and the tools it needs. Domain-specific; never restate generic assistant behavior.

## Multi-agent team
2–5 complementary members and a synthesizer. Pick the mode:
| Mode | Use when | Flow |
| --- | --- | --- |
| Sequential | A pipeline (research → draft → edit) | Each member improves the previous output. |
| Parallel | Independent perspectives | Members answer alone; the synthesizer merges. |
| Router | Many specialists, one needed | A lead picks the single best member. |
| Debate | Decisions with trade-offs | Members critique each other; the synthesizer decides. |

## Harness
The runtime around the model:
- **Allowed tools** — an allow-list enforced by the host; tools not listed are hidden from the model, so they cannot be called. Prompt rules alone are not access control.
- **Skills and agents** switched on for the session.
- **Context budget** and **compaction** of long tool outputs (keep short results verbatim, cut long ones).
- **Approval policy** for risky actions and **operating rules** for every answer.
