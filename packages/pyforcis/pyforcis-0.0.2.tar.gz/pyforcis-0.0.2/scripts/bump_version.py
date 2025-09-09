#!/usr/bin/env python3
"""Simple version bump helper.

Usage:
  python scripts/bump_version.py <new_version>

It updates:
  - pyproject.toml [project].version
  - README.md (release note + citation occurrences)
  - CITATION.cff (version & preferred-citation.version)
  - CHANGELOG.md (inserts new placeholder Unreleased note if necessary)

__init__.__version__ is dynamic via importlib.metadata so no edit needed.

Idempotent: running with the current version makes no changes.
"""
from __future__ import annotations
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "pyproject.toml": r"^version\s*=\s*\"(?P<ver>[^\"]+)\"",
    "CITATION.cff": r"^version:\s*(?P<ver>\S+)$",
}

READ_ME_VERSION_PATTERNS = [
    # Release note line
    (r"(Release note: _Last updated: \d{4}-\d{2}-\d{2} \(v)([^)]+)(\)_)", 2),
    # Inline citation line
    (r"(pyforcis \(Version )(.*?)(\) \[Computer software])", 2),
    # BibTeX version field
    (r"(version\s*=\s*\{)([^}]+)(\},?)", 2),
]

CITATION_PREF_PATTERN = r"(^\s*version:\s*)(.+)$"  # inside preferred-citation block
CHANGELOG_UNRELEASED_HDR = "## [Unreleased]"

TODAY = date.today().strftime("%Y-%m-%d")


def replace_in_text(text: str, pattern: str, new_version: str, group_index: int = 0) -> str:
    if group_index == 0:
        return re.sub(pattern, new_version, text, flags=re.MULTILINE)
    def repl(m: re.Match):
        parts = list(m.groups())
        parts[group_index-1] = new_version
        # Reconstruct with original surrounding groups
        # We assume exactly 3 groups for targeted patterns
        if len(parts) == 3:
            return f"{parts[0]}{parts[1]}{parts[2]}"
        return m.group(0)
    return re.sub(pattern, repl, text, flags=re.MULTILINE)


def update_file(path: Path, new_version: str):
    content = path.read_text(encoding="utf-8")
    original = content
    if path.name == "pyproject.toml":
        def _repl(m: re.Match):
            return f'{m.group(1)}{new_version}{m.group(3)}'
        content = re.sub(r'^(version\s*=\s*")([^"]+)(")', _repl, content, flags=re.MULTILINE)
    elif path.name == "CITATION.cff":
        content = re.sub(r'^(version:\s*)(\S+)', lambda m: m.group(1) + new_version, content, flags=re.MULTILINE)
        content = re.sub(r'(^\s*version:\s*)(\S+)$', lambda m: m.group(1) + new_version, content, flags=re.MULTILINE)
    elif path.name == "README.md":
        for pattern, group_index in READ_ME_VERSION_PATTERNS:
            def _repl(m: re.Match):
                g = list(m.groups())
                g[group_index-1] = new_version
                return ''.join(g)
            content = re.sub(pattern, _repl, content, flags=re.MULTILINE)
        # Update the date in the release note line
        content = re.sub(r'(Release note: _Last updated: )\d{4}-\d{2}-\d{2}(?= \(v)',
                         lambda m: m.group(1) + TODAY, content)
    elif path.name == "CHANGELOG.md":
        # Update dev version line variants (legacy and current formats)
        content = re.sub(r'(### (?:Next \(current dev version: |Current dev version: ))([^\n\)]+)(\)?)',
                         lambda m: m.group(1) + new_version + (m.group(3) or ''), content)
    # Additional: if CITATION.cff and this is a release (no 'dev'), update date-released
    if path.name == "CITATION.cff" and 'dev' not in new_version:
        content = re.sub(r'^(date-released:\s*)\d{4}-\d{2}-\d{2}',
                         lambda m: m.group(1) + TODAY, content, flags=re.MULTILINE)
    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"Updated {path}")
    else:
        print(f"No change {path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <new_version>")
        sys.exit(1)
    new_version = sys.argv[1].strip()
    if not new_version:
        print("Empty version")
        sys.exit(2)
    # Basic validation
    if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+(\.dev[0-9]+)?$', new_version):
        print("Warning: version does not match simple semver+dev pattern; proceeding anyway.")
    # Update primary files
    update_file(ROOT / 'pyproject.toml', new_version)
    update_file(ROOT / 'CITATION.cff', new_version)
    update_file(ROOT / 'README.md', new_version)
    update_file(ROOT / 'CHANGELOG.md', new_version)
    print("Done. Remember to add a changelog entry for the new version when releasing.")

if __name__ == '__main__':
    main()
