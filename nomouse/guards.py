"""Rules code enforces on every walk, whoever wrote the path: the recorded journey,
a baseline, or a model.

A walk may never press a control that has no name, or whose name says nothing to a person
who cannot see it. Those checks are deliberately strict and deliberately simple; they are
a floor, not a full accessibility audit.
"""

from __future__ import annotations

import re

from nomouse.announce import Announcement

# Roles a person activates with Enter or Space. Pressing one of these needs a meaningful name.
ACTIONABLE = {"button", "link", "menuitem", "menuitemcheckbox", "menuitemradio", "checkbox", "radio",
              "switch", "tab", "option", "combobox", "treeitem"}
FIELDS = {"textbox", "searchbox", "combobox", "spinbutton"}

# Names that say nothing about what the control does. Matched on the whole name.
_JUNK = re.compile(
    r"""^(
        button|link|icon|image|img|graphic|svg|figure|null|undefined|none|untitled|unnamed|
        click|click\ here|here|\W+|.                   # punctuation only, or one character
      )$
    | ^(icon|ico|img|svg|btn|fa)[-_\s:]               # icon-lock, btn_primary, fa-cart
    | [-_](icon|svg|btn|img)$                          # lock-icon, pay_btn
    | \.(svg|png|jpe?g|gif|webp)$                      # a file name
    """,
    re.IGNORECASE | re.VERBOSE,
)
# A lower-case code identifier such as cta_primary, cta-primary-2 or button3. Case-sensitive,
# so ordinary words with one hyphen ("Sign-in", "e-mail") are not caught.
_IDENTIFIER = re.compile(r"^[a-z]+(_[a-z0-9]+)+$|^[a-z]+(-[a-z0-9]+){2,}$|^[a-z]+[-_]?\d+$")


def is_junk_name(name: str) -> bool:
    text = re.sub(r"\s+", " ", name or "").strip()
    return not text or bool(_JUNK.search(text)) or bool(_IDENTIFIER.match(text))


def press_violation(focused: Announcement) -> str | None:
    """Why pressing the focused control is refused, or None when it is allowed."""
    if focused.role not in ACTIONABLE:
        return None
    if not focused.name.strip():
        return f"pressed a {focused.role} with no name (heard only \"{focused.spoken()}\")"
    if is_junk_name(focused.name):
        return f"pressed a {focused.role} whose name says nothing (\"{focused.name}\")"
    return None
