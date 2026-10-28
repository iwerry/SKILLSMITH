"""Dependency-free SKILLSMITH command-line interface."""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET = re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-]{12,}")
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
    if not desc or len(desc) > 1024:
        issues.append("Description must contain 1–1024 characters")
    if len(body.splitlines()) > 500:
        issues.append("SKILL.md exceeds recommended 500-line limit")
    if not body.strip():
        issues.append("Missing procedural instructions")
    if SECRET.search((path / "SKILL.md").read_text(encoding="utf-8")):
        issues.append("Possible embedded credential; inspect SKILL.md")
    for child in path.rglob("*"):
        if child.is_symlink():
            issues.append(f"Symlink not permitted: {child.relative_to(path)}")
    return issues

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
    desc = f"{purpose.rstrip('.')}. Use when {when[0].lower() + when[1:]}. Do not use for unrelated requests."
    if len(desc) > 1024 or ":" in desc or "#" in desc:
        raise ValueError("Description is too long or contains YAML-sensitive characters; simplify input")
    content = f"""---
name: {name}
description: {desc}
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
- Do not activate for unrelated tasks.
- Ask permission before destructive actions or publication.

## Failure handling
- If essential inputs are missing, request only the missing information.
- If a tool is unavailable, describe a manual fallback; do not invent a result.

## Examples
- Input: A request matching the activation scope. Output: The specified deliverable with a verification summary.
- Input: An incomplete request. Output: The missing requirement and safe next action.

## Verification
Check accuracy, scope, output format and unresolved risks. Customize these checks for the domain.
"""
    (directory / "SKILL.md").write_text(content, encoding="utf-8")
    (directory / "references").mkdir()
    (directory / "references" / "QUALITY.md").write_text("# Quality checklist\n\n" + "\n".join(f"- [ ] {x.title()}" for x in DIMENSIONS) + "\n", encoding="utf-8")
    (directory / "tests").mkdir()
    tests = {"positive_triggers": [f"Please {when}."], "negative_boundaries": ["Perform an unrelated task."],
             "operational_cases": [{"input": "A representative request", "expected": "Verified deliverable"}],
             "note": "Replace these starter tests with at least 5 positive, 3 negative and 3 operational cases."}
    (directory / "tests" / "triggers.json").write_text(json.dumps(tests, indent=2) + "\n", encoding="utf-8")
    print(directory)

def main():
    p = argparse.ArgumentParser(prog="skillsmith", description="Create, validate, audit and package Agent Skills")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create")
    c.add_argument("--name", required=True)
    c.add_argument("--purpose", required=True)
    c.add_argument("--when", required=True)
    c.add_argument("--output", default="generated")
    for command in ("validate", "audit", "package"):
        s = sub.add_parser(command)
        s.add_argument("path", type=Path)
        if command == "package":
            s.add_argument("--output", default="dist")
    a = p.parse_args()
    try:
        if a.command == "create":
            create(a)
            return 0
        issues = validate(a.path)
        if a.command == "audit":
            print(json.dumps({"dimensions": DIMENSIONS, "static_issues": issues,
                              "note": "Human scoring and runtime tests are required."}, indent=2))
        elif a.command == "validate":
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
