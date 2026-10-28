"""Dependency-free SKILLSMITH command-line interface."""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET = re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-]{12,}")
BRANDS = re.compile(r"(?i)\b(claude|anthropic|openai|chatgpt|gpt|gemini|google|copilot)\b")
LINK = re.compile(r"(?:\]\(|`)((?:references|scripts|assets|evals|tests)/[^)`\s]+)")
DIMENSIONS = ["triggering", "focus", "concision", "progressive disclosure", "executability",
              "reliability", "examples", "robustness", "portability", "security",
              "maintainability", "testability"]

def metadata(path):
    data = (path / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", data, re.S)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter delimited by ---")
    header = {}
    for line in match.group(1).splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            header[key.strip()] = value.strip().strip('"').strip("'")
    return header, data[match.end():]

def validate(path):
    """Return a list of blocking issues (empty list = valid)."""
    issues = []
    if not (path / "SKILL.md").is_file():
        return ["Missing SKILL.md"]
    try:
        header, body = metadata(path)
    except (ValueError, UnicodeError) as exc:
        return [str(exc)]
    name, desc = header.get("name", ""), header.get("description", "")
    if not NAME.fullmatch(name) or len(name) > 64 or name != path.name:
        issues.append("Invalid name or directory mismatch")
    if BRANDS.search(name):
        issues.append("Name must not contain AI product or company names")
    if not desc or len(desc) > 1024:
        issues.append("Description must contain 1–1024 characters")
    if "<" in desc or ">" in desc:
        issues.append("Description must not contain < or >")
    if len(body.splitlines()) > 500:
        issues.append("SKILL.md exceeds recommended 500-line limit")
    if not body.strip():
        issues.append("Missing procedural instructions")
    for ref in sorted(set(LINK.findall(body))):
        ref = ref.rstrip(".,;:")
        if ".." in Path(ref).parts:
            issues.append(f"Unsafe reference path: {ref}")
        elif not (path / ref).exists():
            issues.append(f"Referenced file not found: {ref}")
    for child in path.rglob("*"):
        rel = child.relative_to(path)
        if child.is_symlink():
            issues.append(f"Symlink not permitted: {rel}")
        elif child.is_file() and child.stat().st_size < 2_000_000:
            try:
                if SECRET.search(child.read_text(encoding="utf-8")):
                    issues.append(f"Possible embedded credential; inspect {rel}")
            except UnicodeError:
                pass
    return issues

def warnings(path):
    """Non-blocking advice: description quality and test coverage."""
    out = []
    header, body = metadata(path)
    desc = header.get("description", "").lower()
    if "use when" not in desc and "use whenever" not in desc and "use for" not in desc:
        out.append("Description does not say when to use the skill")
    if "do not" not in desc and "not for" not in desc:
        out.append("Description has no negative boundary")
    if "version" not in (path / "SKILL.md").read_text(encoding="utf-8").split("---")[1]:
        out.append("No metadata.version")
    tests = count_tests(path)
    if tests is None:
        out.append("No test suite (evals/tests.yaml or tests/triggers.json)")
    else:
        pos, neg, ops = tests
        if pos < 5: out.append(f"Only {pos} positive trigger(s); aim for 5+")
        if neg < 3: out.append(f"Only {neg} negative trigger(s); aim for 3+")
        if ops < 3: out.append(f"Only {ops} operational case(s); aim for 3+")
    if "## examples" not in body.lower():
        out.append("No Examples section")
    if re.search(r"TODO:(?!`)", body):
        out.append("TODO markers remain")
    return out

def count_tests(path):
    """Count (positive, negative, operational) tests without third-party YAML."""
    ym = path / "evals" / "tests.yaml"
    if ym.is_file():
        counts, current = {"positive_triggers": 0, "negative_triggers": 0, "operational_cases": 0}, None
        for line in ym.read_text(encoding="utf-8").splitlines():
            key = line.split(":")[0].strip()
            if line and not line[0].isspace() and key in counts:
                current = key
            elif current and re.match(r"^\s{0,4}- ", line):
                counts[current] += 1
        return counts["positive_triggers"], counts["negative_triggers"], counts["operational_cases"]
    js = path / "tests" / "triggers.json"
    if js.is_file():
        data = json.loads(js.read_text(encoding="utf-8"))
        return (len(data.get("positive_triggers", [])),
                len(data.get("negative_boundaries", data.get("negative_triggers", []))),
                len(data.get("operational_cases", [])))
    return None

def audit(path):
    """Heuristic 1–5 scores per rubric dimension, from the files alone."""
    issues = validate(path)
    if issues and issues[0].startswith(("Missing SKILL.md", "SKILL.md must")):
        return {"static_issues": issues}
    header, body = metadata(path)
    low, desc = body.lower(), header.get("description", "").lower()
    warn = warnings(path)
    lines = len(body.splitlines())
    support = [p for p in path.rglob("*") if p.is_file() and p.name != "SKILL.md"]
    tests = count_tests(path) or (0, 0, 0)
    def clamp(x): return max(1, min(5, x))
    s = {
        "triggering": clamp(1 + ("use when" in desc or "use whenever" in desc) * 2 + ("do not" in desc or "not for" in desc) + ("even if" in desc or len(desc) > 200)),
        "focus": clamp(5 - max(0, (low.count("\n## ") - 10) // 3)),
        "concision": clamp(5 if lines <= 300 else 4 if lines <= 500 else 2),
        "progressive disclosure": clamp(2 + bool(support) + bool(LINK.search(body)) + (lines <= 300)),
        "executability": clamp(1 + bool(re.search(r"^1\. ", body, re.M)) * 2 + ("## inputs" in low or "input" in low) + ("output" in low)),
        "reliability": clamp(2 + any(p.parent.name == "scripts" for p in support) + ("verif" in low or "check" in low) + ("template" in low or "schema" in low)),
        "examples": clamp(1 + min(4, low.count("input:") + low.count("→") + low.count("->"))),
        "robustness": clamp(2 + ("missing" in low) + ("ambiguous" in low or "malformed" in low or "invalid" in low) + ("fallback" in low)),
        "portability": clamp(3 + ("fallback" in low or "manual" in low) + ("compatibility" in (path / "SKILL.md").read_text(encoding="utf-8")[:600]) - bool(BRANDS.search(low.split("## ")[0]))),
        "security": clamp(5 - 3 * any("credential" in i for i in issues) - ("permission" not in low and "confirm" not in low and "ask before" not in low)),
        "maintainability": clamp(3 + ("No metadata.version" not in warn) + bool(re.search(r"author", (path / "SKILL.md").read_text(encoding="utf-8")[:600])) - ("TODO markers remain" in warn)),
        "testability": clamp(1 + (tests[0] >= 5) + (tests[0] > 0) + (tests[1] >= 3) + (tests[2] >= 3)),
    }
    avg = round(sum(s.values()) / len(s), 2)
    return {"skill": header.get("name"), "scores": s, "average": avg,
            "ready": avg >= 4.5 and min(s.values()) >= 4 and not issues,
            "static_issues": issues, "warnings": warn,
            "note": "Heuristic scores from files only; run the trigger and operational tests with a real model before publishing."}

def create(args):
    name = args.name
    if not NAME.fullmatch(name) or len(name) > 64:
        raise ValueError("Name must be 1–64 lowercase letters, numbers and single hyphens")
    directory = Path(args.output) / name
    directory.mkdir(parents=True, exist_ok=False)
    purpose = args.purpose.replace("\n", " ").strip()
    when = args.when.replace("\n", " ").strip()
    if not purpose or not when:
        raise ValueError("Purpose and when must be nonempty")
    not_for = (getattr(args, "not_for", None) or "unrelated requests").replace("\n", " ").strip().rstrip(".")
    desc = f"{purpose.rstrip('.')}. Use when {when[0].lower() + when[1:]}, even if they do not name the task. Do not use for {not_for}."
    if len(desc) > 1024 or ":" in desc or "#" in desc or "<" in desc or ">" in desc:
        raise ValueError("Description is too long or contains YAML-sensitive characters; simplify input")
    content = f"""---
name: {name}
description: "{desc}"
license: MIT
metadata:
  author: Daniel Rodrigues
  version: "0.1.0"
---

# {name.replace('-', ' ').title()}

## Objective
{purpose}

## Inputs
- User request and source materials relevant to this task.
- Required output format and constraints.

## Procedure
1. Inspect the request, inputs and any missing requirements.
2. Determine the appropriate domain-specific workflow before execution.
3. Produce the requested deliverable while preserving source accuracy.
4. Verify the result against the requested constraints.
5. Report output, assumptions and any unverified limitations.

## Boundaries
- Activate when {when}.
- Do not activate for {not_for}.
- Ask permission before destructive actions or publication.

## Failure handling
- If essential inputs are missing, request only the missing information.
- If inputs are ambiguous or malformed, state the assumption you take or ask one question.
- If a tool is unavailable, describe a manual fallback; do not invent a result.

## Examples
- Input: A request matching the activation scope. Output: The specified deliverable with a verification summary.
- Input: An incomplete request. Output: The missing requirement and safe next action.
- Input: A request for {not_for}. Output: Do not activate.

Read `references/QUALITY.md` before delivering.

## Verification
Check accuracy, scope, output format and unresolved risks. Customize these checks for the domain.
"""
    (directory / "SKILL.md").write_text(content, encoding="utf-8")
    (directory / "references").mkdir()
    (directory / "references" / "QUALITY.md").write_text("# Quality checklist\n\n" + "\n".join(f"- [ ] {x.title()}" for x in DIMENSIONS) + "\n", encoding="utf-8")
    (directory / "tests").mkdir()
    tests = {"positive_triggers": [f"Please {when}."], "negative_boundaries": [f"Help me with {not_for}."],
             "operational_cases": [{"input": "A representative request", "expected": "Verified deliverable"}],
             "note": "Replace these starter tests with at least 5 positive, 3 negative and 3 operational cases."}
    (directory / "tests" / "triggers.json").write_text(json.dumps(tests, indent=2) + "\n", encoding="utf-8")
    (directory / "evals").mkdir()
    (directory / "evals" / "tests.yaml").write_text(
        f"skill_name: {name}\n"
        "# Fill in: 5+ positive triggers, 3+ near misses, 3+ operational cases.\n"
        "positive_triggers:\n"
        f"  - prompt: \"Please {when}.\"\n    expected_action: \"ACTIVATED\"\n"
        "negative_triggers:\n"
        f"  - prompt: \"Help me with {not_for}.\"\n    expected_action: \"NOT_ACTIVATED\"\n"
        "operational_cases:\n"
        "  - test_id: \"TC-01\"\n    input: \"A representative request\"\n"
        "    verification_criteria:\n      - \"Output follows the documented contract.\"\n", encoding="utf-8")
    print(directory)

def main():
    p = argparse.ArgumentParser(prog="skillsmith", description="Create, validate, audit and package Agent Skills")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create")
    c.add_argument("--name", required=True)
    c.add_argument("--purpose", required=True)
    c.add_argument("--when", required=True)
    c.add_argument("--not-for", dest="not_for", help="Negative boundary, e.g. 'equipment shopping'")
    c.add_argument("--output", default="generated")
    for command in ("validate", "audit", "package"):
        s = sub.add_parser(command)
        s.add_argument("path", type=Path)
        if command == "validate":
            s.add_argument("--strict", action="store_true", help="Treat warnings as failures")
        if command == "package":
            s.add_argument("--output", default="dist")
    a = p.parse_args()
    try:
        if a.command == "create":
            create(a)
            return 0
        a.path = a.path.resolve()
        issues = validate(a.path)
        if a.command == "audit":
            report = audit(a.path)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if not issues else 1
        elif a.command == "validate":
            warn = warnings(a.path) if not issues else []
            for w in warn:
                print(f"WARN: {w}")
            if a.strict and warn:
                issues = warn
            print("PASS" if not issues else "\n".join(issues))
        elif not issues:
            output = Path(a.output)
            output.mkdir(parents=True, exist_ok=True)
            target = output / (a.path.name + ".zip")
            with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(a.path.rglob("*")):
                    if f.is_file():
                        z.write(f, arcname=str(Path(a.path.name) / f.relative_to(a.path)))
            print(target)
        else:
            print("\n".join(issues), file=sys.stderr)
        return 1 if issues else 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
