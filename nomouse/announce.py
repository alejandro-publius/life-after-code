"""What a screen reader would announce for one accessibility node.

The input is a node from Chromium's accessibility tree (the Chrome DevTools Protocol
Accessibility domain): the same computed role, name, value and states that Chromium hands
to screen readers. The wording ("edit text", "check box") is our own neutral rendering;
real screen readers phrase things differently, so this is a simulation, labelled as such.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re

ROLE_WORDS = {
    "button": "button", "link": "link", "textbox": "edit text", "searchbox": "search edit text",
    "combobox": "combo box", "checkbox": "check box", "radio": "radio button", "switch": "switch",
    "menuitem": "menu item", "option": "option", "tab": "tab", "slider": "slider",
    "spinbutton": "spin button", "heading": "heading", "dialog": "dialog", "listbox": "list box",
    "image": "image", "img": "image",
}
NO_FOCUS_ROLES = {"RootWebArea", "WebArea", "document", "generic", "none", "presentation", ""}


def _plain(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


@dataclass(frozen=True)
class Announcement:
    role: str
    name: str = ""
    value: str = ""
    level: int | None = None
    states: tuple[str, ...] = field(default_factory=tuple)
    node: str = ""  # backend node id, used only to notice that focus came back to the same element
    visible: str = ""  # the text a sighted person sees on the control; checked, never spoken

    @property
    def is_page(self) -> bool:
        """Focus is on the page itself, not on a control."""
        return self.role in NO_FOCUS_ROLES

    def spoken(self) -> str:
        if self.is_page:
            return f"{self.name}, page" if self.name else "page"
        word = ROLE_WORDS.get(self.role, self.role)
        if self.role == "heading" and self.level:
            word = f"heading level {self.level}"
        parts = [part for part in (self.name, self.value if self.role in ("textbox", "searchbox", "combobox", "spinbutton") else "") if part]
        parts.append(word)
        parts.extend(self.states)
        return ", ".join(parts)

    def as_dict(self) -> dict:
        data = {"role": self.role, "name": self.name, "spoken": self.spoken()}
        if self.value:
            data["value"] = self.value
        if self.states:
            data["states"] = list(self.states)
        return data


def _prop(node: dict, name: str):
    for item in node.get("properties", []) or []:
        if item.get("name") == name:
            return (item.get("value") or {}).get("value")
    return None


def from_ax_node(node: dict) -> Announcement:
    """Turn one CDP AXNode into an Announcement."""
    role = _plain(str((node.get("role") or {}).get("value", "")))
    name = _plain(str((node.get("name") or {}).get("value", "")))
    value = _plain(str((node.get("value") or {}).get("value", ""))) if node.get("value") else ""
    states: list[str] = []
    for key, word_true, word_false in (
        ("expanded", "expanded", "collapsed"),
        ("checked", "checked", "not checked"),
        ("pressed", "pressed", "not pressed"),
    ):
        state = _prop(node, key)
        if state in (True, "true"):
            states.append(word_true)
        elif state in (False, "false"):
            states.append(word_false)
        elif state == "mixed":
            states.append("partly checked")
    for key, word in (("required", "required"), ("disabled", "dimmed"), ("invalid", "invalid entry")):
        state = _prop(node, key)
        if state in (True, "true") or (key == "invalid" and state not in (None, False, "false")):
            states.append(word)
    level = _prop(node, "level")
    return Announcement(
        role=role, name=name, value=value, level=int(level) if level else None,
        states=tuple(states), node=str(node.get("backendDOMNodeId", node.get("nodeId", ""))),
    )
