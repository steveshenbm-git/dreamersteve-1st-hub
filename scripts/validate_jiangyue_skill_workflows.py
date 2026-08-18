#!/usr/bin/env python3
"""Validate Jiangyue website skill workflow contracts and reference reachability."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SKILLS = {
    "skill_director": ROOT
    / "plugins/jiangyue-skill-director/skills/jiangyue-skill-director",
    "workflow": ROOT
    / "plugins/jiangyue-website-workflow-director/skills/jiangyue-website-workflow-director",
    "planner": ROOT
    / "plugins/jiangyue-website-planner/skills/jiangyue-website-planner",
    "imagegen": ROOT
    / "plugins/jiangyue-website-imagegen/skills/jiangyue-website-imagegen",
    "curator": ROOT
    / "plugins/jiangyue-knowledge-curator/skills/jiangyue-knowledge-curator",
}

REQUIRED_FRAGMENTS = {
    "skill_director": [
        "Worktree Identity Gate",
        "rev-parse --show-toplevel",
        "branch --show-current",
    ],
    "workflow": [
        "Current user production authorization",
        "Whole-Image Synthesis Contract",
        "Scene Invariant Trace",
        "Planner PROCEED -> current user production authorization -> Imagegen READY",
        "Production Lane State",
        "Magnific formal production",
    ],
    "planner": [
        "Provisional Whole-Image Hypothesis",
        "Formal whole-image contract",
        "Reverse consistency check",
        "defined / executable / no known conflict",
    ],
    "imagegen": [
        "Strategy readiness: READY / BLOCKED",
        "Current user production authorization: confirmed / missing",
        "Whole-image synthesis: pass / fail / unverified",
        "/Users/lirongjing/Documents/JY TECH WEB/outputs/jiangyue-website-images",
        "{page-or-type}-{image-role}-{option-code}-draft-{number}",
        "Production lane: test / formal / deterministic",
        "Magnific Formal Execution Package",
        "Provider return status",
    ],
}

FORBIDDEN_ACTIVE_FRAGMENTS = {
    "workflow": [],
    "planner": ["all three factor passes"],
    "imagegen": [
        "READY is authorization to execute",
        "inherited `pass` decision",
        "{conversation-root-cn}",
    ],
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]+)?\)")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []

    for name, skill_dir in SKILLS.items():
        skill_path = skill_dir / "SKILL.md"
        check(skill_path.is_file(), f"{name}: missing SKILL.md", failures)
        if not skill_path.is_file():
            continue

        skill_text = skill_path.read_text(encoding="utf-8")
        frontmatter_match = FRONTMATTER_RE.match(skill_text)
        check(frontmatter_match is not None, f"{name}: invalid or missing YAML frontmatter", failures)
        if frontmatter_match:
            frontmatter: dict[str, str] = {}
            unexpected_structure = False
            for line in frontmatter_match.group(1).splitlines():
                if not line.strip() or line.startswith((" ", "\t")):
                    continue
                if ":" not in line:
                    unexpected_structure = True
                    continue
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
            check(not unexpected_structure, f"{name}: unsupported frontmatter structure", failures)
            check(
                set(frontmatter) <= ALLOWED_FRONTMATTER_KEYS,
                f"{name}: unexpected frontmatter key(s): {sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS)}",
                failures,
            )
            skill_name = frontmatter.get("name", "")
            description = frontmatter.get("description", "")
            check(bool(skill_name), f"{name}: missing frontmatter name", failures)
            check(bool(description), f"{name}: missing frontmatter description", failures)
            check(
                bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name)) and len(skill_name) <= 64,
                f"{name}: invalid skill name: {skill_name}",
                failures,
            )
            check(skill_name == skill_dir.name, f"{name}: skill name does not match directory", failures)
            check(
                "<" not in description and ">" not in description and len(description) <= 1024,
                f"{name}: invalid frontmatter description",
                failures,
            )
        for fragment in REQUIRED_FRAGMENTS.get(name, []):
            check(fragment in skill_text, f"{name}: missing required fragment: {fragment}", failures)
        active_instruction_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in skill_dir.rglob("*.md")
            if "pressure-scenarios" not in path.name
        )
        for fragment in FORBIDDEN_ACTIVE_FRAGMENTS.get(name, []):
            check(
                fragment not in active_instruction_text,
                f"{name}: forbidden active fragment remains: {fragment}",
                failures,
            )

        direct_reference_links: set[Path] = set()
        for target in LINK_RE.findall(skill_text):
            if "://" in target or target.startswith("/"):
                continue
            resolved = (skill_dir / target).resolve()
            check(resolved.exists(), f"{name}: broken local link: {target}", failures)
            try:
                relative = resolved.relative_to(skill_dir.resolve())
            except ValueError:
                continue
            if relative.parts and relative.parts[0] == "references" and resolved.suffix == ".md":
                direct_reference_links.add(resolved)

        for markdown_path in skill_dir.rglob("*.md"):
            markdown_text = markdown_path.read_text(encoding="utf-8")
            for target in LINK_RE.findall(markdown_text):
                if "://" in target or target.startswith("/"):
                    continue
                resolved = (markdown_path.parent / target).resolve()
                check(
                    resolved.exists(),
                    f"{name}: broken local link in {markdown_path.relative_to(skill_dir)}: {target}",
                    failures,
                )

        reference_dir = skill_dir / "references"
        if reference_dir.is_dir():
            reference_files = {path.resolve() for path in reference_dir.glob("*.md")}
            for orphan in sorted(reference_files - direct_reference_links):
                failures.append(f"{name}: reference is not directly reachable from SKILL.md: {orphan.name}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: Jiangyue website skill workflow contracts are coherent and all references are reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
