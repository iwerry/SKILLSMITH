# Portability

| Host | Install | Notes |
| --- | --- | --- |
| Claude (apps, Claude Code, API) | ZIP upload, or the folder in `.claude/skills/` (project) / `~/.claude/skills/` (user) | Runs scripts in a sandbox; declare requirements in `compatibility`. |
| ChatGPT / Codex | Upload the folder or ZIP where skills are supported | Static security checks on upload; avoid undeclared network calls. |
| Gemini | Import SKILL.md and attachments where skills are supported | May not run scripts: the manual fallback matters. |
| Orbi | Creator Studio → Import, or `/skill-creator` | Loads only name + description until the skill is needed. |

## Golden rule
Use generic wording ("run the validation script") and give a manual alternative for every script:

```markdown
Step 3 — Normalize amounts
- With code execution: `python3 scripts/normalize.py --input data.json`
- Without code execution: divide every `amount_cents` by 100 and format with two decimals.
```
