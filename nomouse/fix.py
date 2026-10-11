"""Apply a proposed template fix as a new variant, so code can replay the fixed page.

A fix is untrusted text from a baseline or a model. It never touches the repository's own
templates or the variant it was proposed for: it is written into a new variant directory
next to the original, and the walk is replayed there. Only replay says whether it helped.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from nomouse.proposal import MAX_FIX_CHARS, Fix

NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")  # the shop's own rule for variant names
_PAGE = r"([a-z0-9][a-z0-9_-]{0,47}\.html)"
BASE_PATH = re.compile(rf"nomouse/shop/templates/{_PAGE}")
VARIANT_PATH = re.compile(rf"nomouse/variants/([a-z0-9][a-z0-9-]{{0,47}})/templates/{_PAGE}")
MAX_TEMPLATES = 40
MAX_TEMPLATE_BYTES = 200_000
RECORD = "fix.json"  # what was applied, kept next to the templates for a person to read


class FixError(ValueError):
    """The fix cannot be applied as given. Nothing is written."""


def fixed_name(variant: str, fix: Fix) -> str:
    """The new variant's name: the original's name plus a short hash of the fix."""
    digest = hashlib.sha256(json.dumps([variant, fix.file, fix.find, fix.replace]).encode("utf-8")).hexdigest()
    name = f"{variant[:30]}-fix-{digest[:8]}".lower()
    if not NAME.match(name):
        raise FixError(f"cannot name a fixed variant for {variant!r}")
    return name


def _page_of(fix: Fix, variant: str) -> tuple[str, bool]:
    """(page file name, whether the fix names the shop's base template)."""
    base = BASE_PATH.fullmatch(fix.file)
    if base:
        return base.group(1), True
    override = VARIANT_PATH.fullmatch(fix.file)
    if override and override.group(1) == variant:
        return override.group(2), False
    raise FixError("fix.file must be nomouse/shop/templates/<page>.html or "
                   f"nomouse/variants/{variant}/templates/<page>.html")


def _read(path: Path, root: Path) -> str:
    """A template's text, refusing links and anything that resolves outside root."""
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise FixError(f"{path.name} is not a plain template file")
    if path.stat().st_size > MAX_TEMPLATE_BYTES:
        raise FixError(f"{path.name} is larger than {MAX_TEMPLATE_BYTES} bytes")
    return path.read_text(encoding="utf-8")


def _variant_templates(variant_dir: Path) -> dict[str, str]:
    templates = variant_dir / "templates"
    if not templates.is_dir():
        return {}
    files = sorted(templates.iterdir())
    if len(files) > MAX_TEMPLATES:
        raise FixError(f"{variant_dir.name} has more than {MAX_TEMPLATES} templates")
    return {path.name: _read(path, variant_dir) for path in files if path.suffix == ".html"}


def _occurrences(text: str, find: str, limit: int = 2) -> int:
    """How many times find occurs, overlapping matches included, counting at most limit."""
    count, start = 0, text.find(find)
    while start >= 0 and count < limit:
        count += 1
        start = text.find(find, start + 1)
    return count


def apply_fix(variants_root: Path, variant: str, fix: Fix, repo_root: Path) -> str:
    """Write the fixed page as a new variant under variants_root and return its name."""
    if not isinstance(variant, str) or not NAME.match(variant):
        raise FixError(f"not a variant name: {variant!r}")
    if not fix.find or len(fix.find) > MAX_FIX_CHARS or len(fix.replace) > MAX_FIX_CHARS:
        raise FixError(f"fix.find must be non-empty and both sides at most {MAX_FIX_CHARS} characters")
    page, names_base = _page_of(fix, variant)
    root = Path(variants_root).resolve()
    source_dir = root / variant
    if not source_dir.is_dir():
        raise FixError(f"no variant {variant} under {root}")
    files = _variant_templates(source_dir)
    if not names_base and page not in files:
        raise FixError(f"{variant} does not override {page}")
    if page not in files:
        base_templates = (Path(repo_root) / "nomouse" / "shop" / "templates").resolve()
        files[page] = _read(base_templates / page, base_templates)
    # When the fix names a base template that the variant overrides, the variant's copy is
    # what the shop serves, so that is the page the fix has to work on.
    found = _occurrences(files[page], fix.find)
    if found != 1:
        raise FixError(f"fix.find occurs {'more than once' if found else 'nowhere'} in {page}; it must occur once")
    files[page] = files[page].replace(fix.find, fix.replace, 1)
    record = json.dumps({"from": variant, "file": fix.file, "find": fix.find, "replace": fix.replace},
                        ensure_ascii=False, indent=1) + "\n"

    name = fixed_name(variant, fix)
    target = root / name
    if target.is_symlink():
        raise FixError(f"{name} already exists as a link")
    if target.exists():
        if _variant_templates(target) == files:
            return name  # the same fix was already applied to the same pages
        raise FixError(f"{name} already exists with different templates")
    (target / "templates").mkdir(parents=True)
    for file_name, text in files.items():
        (target / "templates" / file_name).write_text(text, encoding="utf-8")
    (target / RECORD).write_text(record, encoding="utf-8")
    return name
