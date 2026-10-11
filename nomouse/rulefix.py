"""F0: a fixer for a broken No Mouse walk made only of simple template rules, with no model.

Why: the bench compares a model's template fix with a fixer that needs no model, on barriers
neither has seen before. F0 has to be an honest, strong baseline and not a strawman, so it knows
the common keyboard and screen reader barriers and fixes the one tied to the step that failed.

F0 sees only what the model sees: the journey (the failed find step gives the expected role and
name), the failed step, what Tab reached on the broken page (role, name and visible text), the
failure reason, and the page template's path and source. It returns one find/replace whose find
occurs exactly once in that source, or None, with a short reason naming the rule that fired or
saying why none did. It is deterministic and opens no browser and no network connection.

The rules, tried first on the control the walk expected and then on any control on the page:

1. A div or span that only a mouse click operates becomes a real button (type="submit" when it
   submits a form, else type="button"), or a real link when a link was expected and its handler
   only navigates. id, class and onclick are kept; role and tabindex are dropped.
2. role="button" or role="link" on an element that Tab never reaches or Enter cannot operate gets
   the same treatment. Extras of the same kind: a native control taken out of the tab order by a
   negative tabindex, a link used as a button, and a button used as a link.
3. An unnamed button or link gets aria-label set to the expected name, when the expected role
   matches. Among several, the submit control wins when the expected control submits a form.
4. A junk image alt (a file name, say) inside a button or link gets the expected name, or alt=""
   when the control already shows text.
5. An aria-label (or aria-labelledby) that leaves out the visible label (WCAG 2.5.3), or is junk
   while visible text exists, is removed so the visible text names the control.
6. A junk aria-label on a control with no visible text gets the expected name.
7. Labels whose for= points at a field other than the one right after them are corrected, all
   pairs in one find.
8. An unlabelled field gets a label: plain text right before it that equals the expected name
   becomes <label for=...>, otherwise the field gets aria-label set to the expected name.
9. Anything else (a dialog that traps focus, say) returns None, with the reason.

One extra, numbered 10: when the failed step is a heading check, a heading hidden by aria-hidden,
a heading that is only an image with a junk alt, or plain text that only looks like the expected
heading is made a real heading again.

Templates are string.Template files: $placeholders such as $price are never rewritten, and they
match any text when template text is compared with what was heard on the rendered page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import html
import re

from nomouse.guards import ACTIONABLE, FIELDS, is_junk_name
from nomouse.journey import Journey, Result
from nomouse.proposal import MAX_FIX_CHARS, Fix

MAX_SOURCE_CHARS = 200_000  # the limit fix.py puts on one template file
MAX_ELEMENTS = 5_000
MAX_WALK = 20_000  # nodes one tree or text walk may visit
MAX_DEPTH = 200  # ancestors followed from one element
MAX_HEARD = 60  # the walker's own limit on the tab order it records
MAX_ATTR_TEXT = 120  # longest nearby text F0 will copy into an alt

VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
                  "source", "track", "wbr"})
RAW_TEXT = frozenset({"script", "style", "textarea", "title"})
CLOSES_P = frozenset({"address", "article", "aside", "blockquote", "details", "div", "dl", "fieldset", "figure",
                      "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "main", "nav", "ol",
                      "p", "pre", "section", "table", "ul"})
BLOCK = CLOSES_P | {"br", "dd", "dt", "label", "li", "td", "th", "tr"}
NO_TEXT = frozenset({"head", "iframe", "img", "noscript", "object", "option", "script", "select", "style", "svg",
                     "template", "textarea", "title"})
CONVERTIBLE = frozenset({"a", "b", "div", "em", "i", "p", "small", "span", "strong", "u"})
TEXT_HOLDERS = frozenset({"b", "div", "em", "p", "small", "span", "strong"})
INTERACTIVE = frozenset({"button", "details", "iframe", "input", "select", "summary", "textarea"})
NAMED_ROLES = ("button", "link")
CONTROL_ROLES = frozenset(ACTIONABLE | set(NAMED_ROLES))
FIELD_ROLES = frozenset(FIELDS | {"checkbox", "listbox", "radio"})
NOT_FIELD_INPUTS = frozenset({"button", "hidden", "image", "reset", "submit"})
KEY_HANDLERS = ("onkeydown", "onkeyup", "onkeypress")
STOP_WORDS = frozenset({"and", "for", "from", "here", "into", "now", "that", "the", "this", "with", "you", "your"})
ELSEWHERE = "; it is not matched to the control the walk expected"

_TAG = re.compile(
    r"""<!--.*?-->|<![^>]*>|<\?[^>]*>"""
    r"""|</([a-zA-Z][\w:-]*)\s*>"""
    r"""|<([a-zA-Z][\w:-]*)((?:\s+[^\s"'<>/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]+))?)*)\s*(/?)>""",
    re.S)
_ATTR = re.compile(r"""\s+([^\s"'<>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?""")
_SPACE = re.compile(r"\s*")
# string.Template placeholders: $name, ${name}, and $$ for a plain dollar sign.
_PLACEHOLDER = re.compile(r"\$(?:\$|\{[_a-zA-Z][_a-zA-Z0-9]*\}|[_a-zA-Z][_a-zA-Z0-9]*)")
_SLOT = "\x00"
_NAVIGATION = re.compile(r"""location(?:\.href)?\s*=\s*(["'])([^"'\s<>]{1,300})\1"""
                         r"""|location\.(?:assign|replace)\(\s*(["'])([^"'\s<>]{1,300})\3""")
_SUBMIT_WORDS = re.compile(r"\b(pay|place order|order|buy|purchase|checkout|check out|submit|confirm|continue|"
                           r"add to (cart|bag|basket)|sign in|log in|save|send|search)\b")


# Small text helpers. Template text keeps its $placeholders; heard text is the rendered page.

def _fold(text: str) -> str:
    return " ".join((text or "").split()).casefold()


def _slots(text: str) -> str:
    """Template text with each $placeholder as one slot character ($$ is a plain dollar sign)."""
    return _PLACEHOLDER.sub(lambda m: "$" if m.group(0) == "$$" else _SLOT, text or "")


def _same(template_text: str, heard: str) -> bool:
    """Whether template text, once its placeholders are filled, can read exactly as the heard text."""
    if not heard.strip():
        return False
    pattern = ".+?".join(re.escape(part) for part in _fold(_slots(template_text)).split(_SLOT))
    return re.fullmatch(pattern, _fold(heard), re.S) is not None


def _words(text: str) -> str:
    return " ".join(re.sub(r"[^0-9a-z]+", " ", (text or "").casefold()).split())


def _label_in_name(visible: str, name: str) -> bool:
    """guards.label_not_in_name, inverted and read on template text: a placeholder matches any words."""
    parts = [part for part in (_words(piece) for piece in _slots(visible).split(_SLOT)) if part]
    if not parts:
        return True  # only placeholders: nothing to judge, so do not flag it
    pattern = ".*?".join(re.escape(part) for part in parts)
    return re.search(pattern, _words(_slots(name).replace(_SLOT, " slot "))) is not None


def _tokens(text: str) -> set[str]:
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", text or "")
    return {word for word in re.findall(r"[a-z]+", spaced.casefold()) if len(word) >= 3} - STOP_WORDS


def _attr(name: str, value: str) -> str:
    return f' {name}="{html.escape(value, quote=True)}"'


def _short(text: str, limit: int = 60) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


# A small, forgiving HTML reader that keeps exact source offsets.

class _TooLarge(Exception):
    """The template has more elements than F0 will read."""


@dataclass
class _El:
    tag: str
    raw_name: str
    start: int  # offset of "<"
    open_end: int  # just after the start tag's ">"
    attrs_end: int  # just after the last attribute
    attrs: dict[str, str]  # lower-case names, unescaped values, first occurrence wins
    spans: list[tuple[str, int, int]]  # (name, start, end) of each attribute, leading space included
    parent: int | None
    close_start: int = -1
    end: int = -1
    closed: bool = False  # closed by its own end tag, or void, or self-closing
    children: list = field(default_factory=list)  # element indexes and (start, end) text spans


def _input_type(el: _El) -> str:
    return el.attrs.get("type", "text").strip().lower() or "text"


def _is_image(el: _El) -> bool:
    return el.tag == "img" or (el.tag == "input" and _input_type(el) == "image")


def _is_field(el: _El) -> bool:
    if el.tag in ("select", "textarea"):
        return True
    return el.tag == "input" and _input_type(el) not in NOT_FIELD_INPUTS


def _attr_true(el: _El, name: str) -> bool:
    return el.attrs.get(name, "").strip().lower() == "true"


def _explicit_role(el: _El) -> str:
    words = el.attrs.get("role", "").split()
    role = words[0].lower() if words else ""
    return "" if role in ("presentation", "none", "generic") else role


def _native_role(el: _El) -> str:
    if el.tag == "a":
        return "link" if "href" in el.attrs else ""
    if el.tag in ("button", "summary"):
        return "button"
    if el.tag == "textarea":
        return "textbox"
    if el.tag == "select":
        size = el.attrs.get("size", "").strip()
        return "listbox" if "multiple" in el.attrs or (size.isdigit() and int(size) > 1) else "combobox"
    if el.tag == "input":
        kind = _input_type(el)
        roles = {"submit": "button", "button": "button", "reset": "button", "image": "button",
                 "checkbox": "checkbox", "radio": "radio", "number": "spinbutton", "search": "searchbox",
                 "range": "slider", "hidden": ""}
        return roles.get(kind, "combobox" if "list" in el.attrs else "textbox")
    return ""


def _role(el: _El) -> str:
    return _explicit_role(el) or _native_role(el)


def _tabindex(el: _El) -> int | None:
    try:
        return int(el.attrs["tabindex"].strip())
    except (KeyError, ValueError):
        return None


def _natively_focusable(el: _El) -> bool:
    if el.tag in ("button", "input", "select", "textarea") and "disabled" in el.attrs:
        return False
    if el.tag == "input":
        return _input_type(el) != "hidden"
    return (el.tag == "a" and "href" in el.attrs) or el.tag in ("button", "select", "textarea", "summary")


def _focusable(el: _El) -> bool:
    index = _tabindex(el)
    return index >= 0 if index is not None else _natively_focusable(el)


def _handles_enter(el: _El) -> bool:
    code = " ".join(el.attrs.get(name, "") for name in KEY_HANDLERS)
    return bool(re.search(r"Enter|\b13\b", code))


def _nav_url(handler: str) -> str:
    """The address a click handler only navigates to, when it says so plainly."""
    match = _NAVIGATION.search(handler or "")
    url = (match.group(2) or match.group(4)) if match else ""
    return "" if url.lower().startswith(("javascript:", "data:", "vbscript:")) else url


class _Doc:
    def __init__(self, source: str):
        self.source = source
        self.els: list[_El] = []
        self.top: list = []
        self.at: dict[int, int] = {}  # start offset -> element index
        self._parse()
        self.ids: dict[str, int] = {}
        self.labels: dict[str, list[int]] = {}
        for index, el in enumerate(self.els):
            ident = el.attrs.get("id", "").strip()
            if ident:
                self.ids.setdefault(ident, index)
            target = el.attrs.get("for", "").strip()
            if el.tag == "label" and target:
                self.labels.setdefault(target, []).append(index)

    def _parse(self) -> None:
        source, stack, pos = self.source, [], 0

        def add(item) -> None:
            (self.els[stack[-1]].children if stack else self.top).append(item)

        def close(index: int, close_start: int, end: int, own: bool) -> None:
            el = self.els[index]
            el.close_start, el.end, el.closed = close_start, end, own

        for _ in range(len(source) + 1):  # every pass moves pos forward
            match = _TAG.search(source, pos)
            if match is None:
                break
            if match.start() > pos:
                add((pos, match.start()))
            pos = match.end()
            end_name, name = match.group(1), match.group(2)
            if end_name:
                tag = end_name.lower()
                for depth in range(len(stack) - 1, -1, -1):
                    if self.els[stack[depth]].tag == tag:
                        for inner in stack[depth + 1:]:
                            close(inner, match.start(), match.start(), False)
                        close(stack[depth], match.start(), match.end(), True)
                        del stack[depth:]
                        break
                continue
            if not name:
                continue  # a comment, doctype or processing instruction
            if len(self.els) >= MAX_ELEMENTS:
                raise _TooLarge
            tag = name.lower()
            if tag in CLOSES_P and stack and self.els[stack[-1]].tag == "p":
                close(stack.pop(), match.start(), match.start(), False)
            attrs: dict[str, str] = {}
            spans: list[tuple[str, int, int]] = []
            for attr in _ATTR.finditer(match.group(3)):
                key = attr.group(1).lower()
                value = next((v for v in attr.group(2, 3, 4) if v is not None), "")
                spans.append((key, match.start(3) + attr.start(), match.start(3) + attr.end()))
                attrs.setdefault(key, html.unescape(value))
            index = len(self.els)
            self.els.append(_El(tag=tag, raw_name=name, start=match.start(), open_end=match.end(),
                                attrs_end=match.end(3), attrs=attrs, spans=spans,
                                parent=stack[-1] if stack else None))
            add(index)
            self.at[match.start()] = index
            if tag in VOID or match.group(4):
                close(index, match.end(), match.end(), True)
            elif tag in RAW_TEXT:
                ending = re.compile(rf"</{tag}\s*>", re.I).search(source, match.end())
                stop = ending.start() if ending else len(source)
                if stop > match.end():
                    self.els[index].children.append((match.end(), stop))
                close(index, stop, ending.end() if ending else stop, ending is not None)
                pos = ending.end() if ending else len(source)
            else:
                stack.append(index)
        if pos < len(source):
            add((pos, len(source)))
        for index in stack:
            close(index, len(source), len(source), False)

    # Tree walks, all bounded.

    def chain(self, index: int | None) -> list[int]:
        """The element and its ancestors, nearest first."""
        out: list[int] = []
        while index is not None and len(out) < MAX_DEPTH:
            out.append(index)
            index = self.els[index].parent
        return out

    def ancestor(self, index: int, tag: str) -> int | None:
        return next((i for i in self.chain(index)[1:] if self.els[i].tag == tag), None)

    def descendants(self, index: int) -> list[int]:
        out: list[int] = []
        todo = [c for c in reversed(self.els[index].children) if isinstance(c, int)]
        while todo and len(out) < MAX_WALK:
            i = todo.pop()
            out.append(i)
            todo.extend(c for c in reversed(self.els[i].children) if isinstance(c, int))
        return out

    def hidden(self, el: _El) -> bool:
        if "hidden" in el.attrs or el.tag in ("head", "noscript", "template"):
            return True
        if el.tag == "input" and _input_type(el) == "hidden":
            return True
        return bool(re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", el.attrs.get("style", ""), re.I))

    def rendered(self, index: int) -> bool:
        return not any(self.hidden(self.els[i]) for i in self.chain(index))

    def aria_hidden(self, index: int) -> bool:
        return any(_attr_true(self.els[i], "aria-hidden") for i in self.chain(index))

    def text(self, index: int, *, name: bool) -> str:
        """Visible text (name=False) or the accessible name from content (name=True), placeholders kept."""
        out: list[str] = []
        todo = list(reversed(self.els[index].children))
        for _ in range(MAX_WALK):
            if not todo:
                break
            item = todo.pop()
            if isinstance(item, str):
                out.append(item)
                continue
            if isinstance(item, tuple):
                out.append(html.unescape(self.source[item[0]:item[1]]))
                continue
            el = self.els[item]
            if self.hidden(el):
                continue
            if name:
                if _attr_true(el, "aria-hidden"):
                    continue
                label = el.attrs.get("aria-label", "").strip()
                if label:
                    out.append(f" {label} ")
                    continue
                if _is_image(el):
                    if el.attrs.get("role", "").strip().lower() not in ("presentation", "none"):
                        out.append(f" {el.attrs.get('alt', '')} ")
                    continue
                if el.tag == "svg":
                    out.append(f" {self.svg_title(item)} ")
                    continue
            if el.tag == "input":
                if _input_type(el) in ("submit", "button", "reset"):
                    out.append(f" {el.attrs.get('value', '')} ")
                continue
            if el.tag in NO_TEXT:
                continue
            gap = " " if el.tag in BLOCK else ""
            todo.append(gap)
            todo.extend(reversed(el.children))
            todo.append(gap)
        return " ".join("".join(out).split())

    def svg_title(self, index: int) -> str:
        for child in self.els[index].children:
            if isinstance(child, int) and self.els[child].tag == "title":
                return self.text(child, name=False)
        return ""

    def visible(self, index: int) -> str:
        """What a sighted person reads on the control (the walker's innerText, or a button's value)."""
        el = self.els[index]
        if el.tag == "input":
            return el.attrs.get("value", "").strip() if _input_type(el) in ("submit", "button", "reset") else ""
        return self.text(index, name=False)

    def content_name(self, index: int) -> str:
        el = self.els[index]
        if el.tag == "input":
            kind = _input_type(el)
            if kind == "image":
                return el.attrs.get("alt", "").strip()
            if kind in ("submit", "reset"):
                return el.attrs.get("value", "").strip() or kind.title()
            return el.attrs.get("value", "").strip() if kind == "button" else ""
        return self.text(index, name=True)

    def labelledby(self, index: int) -> str | None:
        """The text aria-labelledby points at, or None when it points at nothing in this template."""
        refs = self.els[index].attrs.get("aria-labelledby", "").split()[:10]
        found = [self.ids[ref] for ref in refs if ref in self.ids]
        if not found:
            return None
        return " ".join(self.text(i, name=True) for i in found).strip()

    def would_be_name(self, index: int) -> str:
        """The name the element gets from aria-label, else from its content."""
        return self.els[index].attrs.get("aria-label", "").strip() or self.content_name(index)

    def field_labels(self, index: int) -> list[int]:
        el = self.els[index]
        ident = el.attrs.get("id", "").strip()
        found = list(self.labels.get(ident, [])) if ident else []
        wrap = self.ancestor(index, "label")
        if wrap is not None and wrap not in found and not self.els[wrap].attrs.get("for", "").strip():
            found.append(wrap)
        return found

    def label_text(self, index: int) -> str:
        return " ".join(self.text(i, name=False) for i in self.field_labels(index)).strip()

    def has_submit(self, form: int, besides: int) -> bool:
        """Whether the form has a native submit control other than the element besides (or inside it)."""
        for i in self.descendants(form):
            if besides in self.chain(i):
                continue
            el = self.els[i]
            if el.tag == "button" and el.attrs.get("type", "submit").strip().lower() not in ("button", "reset"):
                return True
            if el.tag == "input" and _input_type(el) in ("submit", "image"):
                return True
        return False

    def retag(self, index: int, *, tag: str | None = None, first: tuple = (), drop: frozenset | set = frozenset(),
              put: dict | None = None) -> str:
        """The element's start tag with attributes added first, dropped or set; the rest kept as written."""
        el = self.els[index]
        put = dict(put or {})
        skip = {name for name, _ in first} | set(drop)
        done: set[str] = set()
        kept: list[str] = []
        for name, start, end in el.spans:
            if name in skip or name in done:
                continue
            if name in put:
                kept.append(_attr(name, put[name]))
                done.add(name)
            else:
                kept.append(self.source[start:end])
        head = "".join(_attr(name, value) for name, value in first)
        added = "".join(_attr(name, value) for name, value in put.items() if name not in done)
        return f"<{tag or el.raw_name}{head}{''.join(kept)}{added}{self.source[el.attrs_end:el.open_end]}"


# What the walk expected, read from the journey and the failed walk.

@dataclass(frozen=True)
class _Goal:
    role: str = ""
    name: str = ""
    heard: bool = False  # a control with this role and name was heard on the broken page
    other_role: str = ""  # the role a control with this name was heard with instead, if any
    submits: bool = False  # the journey presses Enter on it and then expects a new heading
    heading: str = ""  # the heading the failed step expected, when the failed step is a heading check


def _goal(journey: Journey, result: Result) -> _Goal:
    steps, failed = journey.steps, result.failed_step
    if failed is None or not 0 <= failed < len(steps):
        return _Goal()
    heading = steps[failed].name if steps[failed].do == "expect_heading" else ""
    target = next((i for i in range(failed, max(-1, failed - 4), -1) if steps[i].do == "find"), None)
    if target is None:
        return _Goal(heading=heading)
    step = steps[target]
    same = [h for h in result.heard[:MAX_HEARD] if _fold(h.name) == _fold(step.name)]
    after = steps[target + 1] if target + 1 < len(steps) else None
    submits = (step.role == "button" and after is not None and after.do == "press" and after.key == "Enter"
               and any(s.do == "expect_heading" for s in steps[target + 2:]))
    return _Goal(role=step.role, name=step.name, heard=any(h.role == step.role for h in same),
                 other_role=next((h.role for h in same if h.role != step.role), ""), submits=submits,
                 heading=heading)


@dataclass(frozen=True)
class _Edit:
    start: int
    end: int
    new: str
    reason: str


def _count(text: str, sub: str, limit: int = 2) -> int:
    """Occurrences of sub in text, overlapping ones included (as fix.py counts), at most limit."""
    count, start = 0, text.find(sub)
    while start >= 0 and count < limit:
        count += 1
        start = text.find(sub, start + 1)
    return count


def _unique_span(source: str, start: int, end: int) -> tuple[int, int]:
    """The smallest span around [start, end) that occurs once: the span, then whole lines, then more lines."""
    if _count(source, source[start:end]) == 1:
        return start, end
    start = source.rfind("\n", 0, start) + 1
    stop = source.find("\n", end)
    end = len(source) if stop < 0 else stop
    for _ in range(source.count("\n") + 2):
        if _count(source, source[start:end]) == 1:
            return start, end
        if start > 0:
            start = source.rfind("\n", 0, start - 1) + 1
        if end < len(source):
            stop = source.find("\n", end + 1)
            end = len(source) if stop < 0 else stop
    return 0, len(source)


def _make_fix(path: str, source: str, edit: _Edit) -> Fix | None:
    start, end = _unique_span(source, edit.start, edit.end)
    find = source[start:end]
    replace = source[start:edit.start] + edit.new + source[edit.end:end]
    if not find or find == replace or len(find) > MAX_FIX_CHARS or len(replace) > MAX_FIX_CHARS:
        return None
    return Fix(file=path, find=find, replace=replace)


# Rules 1 and 2: controls that Tab or Enter cannot use become real buttons and links.

def _fake(doc: _Doc, index: int) -> str:
    """Why this element has to become a real button or link, or "" when it does not."""
    el = doc.els[index]
    if el.tag not in CONVERTIBLE and "-" not in el.tag:
        return ""
    if (el.tag == "a" and "href" in el.attrs) or not el.closed or el.end <= el.close_start:
        return ""
    if any(doc.els[i].tag in INTERACTIVE or (doc.els[i].tag == "a" and "href" in doc.els[i].attrs)
           for i in doc.descendants(index)):
        return ""  # never nest one control inside another
    role = _explicit_role(el)
    if role in NAMED_ROLES:
        if not _focusable(el):
            return f'a {el.tag} with role="{role}" that Tab never reaches'
        if not _handles_enter(el):
            return f'a {el.tag} with role="{role}" that Enter does not operate'
        return ""
    if role:
        return ""
    return f"a {el.tag} that only a mouse click operates" if "onclick" in el.attrs else ""


def _button_type(doc: _Doc, index: int, *, expected_submit: bool) -> str:
    """submit when the handler submits a form, or when the element is plainly its form's submit control."""
    el = doc.els[index]
    handler = el.attrs.get("onclick", "")
    if re.search("submit", handler, re.I):
        return "submit"
    if "location" in handler:
        return "button"
    form = doc.ancestor(index, "form")
    if form is None or doc.has_submit(form, index):
        return "button"
    if expected_submit or _SUBMIT_WORDS.search(_fold(doc.visible(index))):
        return "submit"
    return "button"


def _is_submit(doc: _Doc, index: int, *, expected_submit: bool) -> bool:
    el = doc.els[index]
    if el.tag == "button":
        kind = el.attrs.get("type", "submit").strip().lower()
        return kind not in ("button", "reset") and doc.ancestor(index, "form") is not None
    if el.tag == "input":
        return _input_type(el) in ("submit", "image")
    return bool(_fake(doc, index)) and _button_type(doc, index, expected_submit=expected_submit) == "submit"


def _convert(doc: _Doc, index: int, want: str, *, expected_submit: bool, label: str = "") -> tuple[str, str]:
    """(new element text, what it became). The content is kept exactly as written."""
    el = doc.els[index]
    drop = frozenset({"role", "tabindex", "type", "href", *KEY_HANDLERS})
    url = _nav_url(el.attrs.get("onclick", ""))
    if want == "link" and url:
        tag, first, became = "a", (("href", url),), f'a link to "{url}"'
    else:
        kind = _button_type(doc, index, expected_submit=expected_submit)
        tag, first = "button", (("type", kind),) + ((("role", "link"),) if want == "link" else ())
        became = f'a <button type="{kind}">' + (' with role="link"' if want == "link" else "")
    opening = doc.retag(index, tag=tag, first=first, drop=drop, put={"aria-label": label} if label else None)
    return opening + doc.source[el.open_end:el.close_start] + f"</{tag}>", became


def _native_tied(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    """Rules 1 and 2 on the element whose name is the expected one, plus the role-swap extras."""
    if goal.role not in NAMED_ROLES:
        return None
    for index, el in enumerate(doc.els):
        if not doc.rendered(index):
            continue
        why = _fake(doc, index)
        if why and _same(doc.would_be_name(index), goal.name):
            new, became = _convert(doc, index, goal.role, expected_submit=goal.submits)
            rule = "rule 2" if _explicit_role(el) else "rule 1"
            return _Edit(el.start, el.end, new, f'{rule}: "{_short(goal.name)}" was {why}; it is now {became}')
    if not goal.other_role:
        return None
    for index, el in enumerate(doc.els):
        if not doc.rendered(index) or _explicit_role(el) or not el.closed or el.end <= el.close_start:
            continue
        if not _same(doc.would_be_name(index), goal.name):
            continue
        href = el.attrs.get("href", "").strip().lower()
        if (goal.role == "button" and el.tag == "a" and "onclick" in el.attrs
                and (href in ("", "#") or href.startswith(("#", "javascript:")))):
            new, became = _convert(doc, index, "button", expected_submit=goal.submits)
            return _Edit(el.start, el.end, new, f"rule 2 (extra): a link was used as a button; it is now {became}")
        if goal.role == "link" and el.tag == "button" and _nav_url(el.attrs.get("onclick", "")):
            new, became = _convert(doc, index, "link", expected_submit=False)
            return _Edit(el.start, el.end, new, f"rule 2 (extra): a button was used as a link; it is now {became}")
    return None


def _native_anywhere(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    """Rules 1 and 2 on the first such element with text anywhere on the page."""
    for index, el in enumerate(doc.els):
        why = _fake(doc, index)
        if not why or not doc.rendered(index) or not doc.visible(index):
            continue
        role = _explicit_role(el)
        want = "link" if role == "link" or (not role and _nav_url(el.attrs.get("onclick", ""))) else "button"
        new, became = _convert(doc, index, want, expected_submit=False)
        rule = "rule 2" if role else "rule 1"
        return _Edit(el.start, el.end, new,
                     f'{rule}: "{_short(doc.visible(index))}" was {why}; it is now {became}{ELSEWHERE}')
    return None


def _tab_order(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    """Rule 2 (extra): the expected native control was taken out of the tab order."""
    if not goal.role or goal.heard:
        return None
    for index, el in enumerate(doc.els):
        value = _tabindex(el)
        if value is None or value >= 0 or not _natively_focusable(el) or _role(el) != goal.role:
            continue
        if _is_field(el):
            name = el.attrs.get("aria-label", "").strip() or doc.label_text(index)
        else:
            name = doc.would_be_name(index)
        if doc.rendered(index) and _same(name, goal.name):
            return _Edit(el.start, el.open_end, doc.retag(index, drop={"tabindex"}),
                         f'rule 2 (extra): tabindex="{value}" kept Tab from reaching "{_short(goal.name)}"; removed it')
    return None


# Rule 5: a name override that leaves out the visible label, or says nothing.

def _override(doc: _Doc, index: int) -> tuple[list[str], str, str] | None:
    """(attributes to remove, the visible label, the overriding name) for one element, or None."""
    el = doc.els[index]
    if _is_field(el):
        visible = doc.label_text(index)
    elif _role(el) in CONTROL_ROLES or _fake(doc, index):
        visible = doc.visible(index)
    else:
        return None
    if not visible.strip():
        return None
    remove: list[str] = []
    via = doc.labelledby(index)
    if via is not None:
        if not is_junk_name(via) and _label_in_name(visible, via):
            return None
        remove.append("aria-labelledby")
    label = el.attrs.get("aria-label", "").strip()
    if label and (is_junk_name(label) or not _label_in_name(visible, label)):
        remove.append("aria-label")
    if not remove:
        return None
    return remove, visible, via if via is not None else label


def _override_rule(doc: _Doc, goal: _Goal, result: Result, *, tied: bool) -> _Edit | None:
    for index, el in enumerate(doc.els):
        if not doc.rendered(index):
            continue
        found = _override(doc, index)
        if found is None:
            continue
        remove, visible, name = found
        if tied and not (_role(el) == goal.role and _same(visible, goal.name)):
            continue
        what = " and ".join(remove)
        why = "says nothing, while it shows" if is_junk_name(name) else "leaves out the visible label"
        return _Edit(el.start, el.open_end, doc.retag(index, drop=set(remove)),
                     f'rule 5: the {_role(el) or "control"}\'s {what} "{_short(name)}" {why} "{_short(visible)}"; '
                     "removed it so the visible label names it" + ("" if tied else ELSEWHERE))
    return None


# Rule 7: labels pointing at the wrong field.

def _label_pairs(doc: _Doc) -> list[tuple[int, str]]:
    """(label, id of the field right after it) for each label whose for= names another field."""
    pairs: list[tuple[int, str]] = []
    for index, el in enumerate(doc.els):
        target = el.attrs.get("for", "").strip()
        if el.tag != "label" or not target or not el.closed:
            continue
        nxt = doc.at.get(_SPACE.match(doc.source, el.end).end())
        if nxt is None or not _is_field(doc.els[nxt]):
            continue
        ident = doc.els[nxt].attrs.get("id", "").strip()
        if ident and ident != target:
            pairs.append((index, ident))
    return pairs


def _labels_rule(doc: _Doc, goal: _Goal, result: Result, *, tied: bool) -> _Edit | None:
    pairs = _label_pairs(doc)
    if not pairs:
        return None
    texts = [doc.text(i, name=False) for i, _ in pairs]
    # Tied when the walk was looking for a field, or for one of these labels, or when a field
    # named by one of them was heard as an invalid entry (a card number typed into the email field).
    invalid = [h.name for h in result.heard[:MAX_HEARD] if h.role in FIELD_ROLES and "invalid entry" in h.states]
    if tied and not ((goal.role in FIELD_ROLES and not goal.heard)
                     or any(_same(text, name) for text in texts for name in [goal.name, *invalid])):
        return None
    start, end = doc.els[pairs[0][0]].start, doc.els[pairs[-1][0]].open_end
    out, cursor = [], start
    for index, ident in pairs:
        el = doc.els[index]
        out.extend([doc.source[cursor:el.start], doc.retag(index, put={"for": ident})])
        cursor = el.open_end
    out.append(doc.source[cursor:end])
    names = ", ".join(f'"{_short(text, 30)}"' for text in texts)
    return _Edit(start, end, "".join(out),
                 f"rule 7: the label(s) {names} pointed at another field; each now names the field right after it"
                 + ("" if tied else ELSEWHERE))


# Rule 8: an unlabelled field.

def _unlabelled(doc: _Doc, index: int) -> bool:
    el = doc.els[index]
    if not _is_field(el) or not doc.rendered(index) or doc.labelledby(index) is not None:
        return False
    label = el.attrs.get("aria-label", "").strip()
    if label and not is_junk_name(label):
        return False
    return not doc.label_text(index)


def _text_before(doc: _Doc, index: int) -> tuple[int, int, str, int | None] | None:
    """(start, end, text, element) of plain text right before the field: a text run, or a p, span or
    div holding only text. None when something else comes first."""
    el = doc.els[index]
    siblings = doc.els[el.parent].children if el.parent is not None else doc.top
    for item in reversed(siblings[:siblings.index(index)]):
        if isinstance(item, tuple):
            raw = doc.source[item[0]:item[1]]
            if not raw.strip():
                continue
            lead = len(raw) - len(raw.lstrip())
            return item[0] + lead, item[0] + len(raw.rstrip()), " ".join(html.unescape(raw).split()), None
        prev = doc.els[item]
        if (prev.tag in TEXT_HOLDERS and prev.closed and prev.end > prev.close_start
                and not any(isinstance(child, int) for child in prev.children)):
            text = doc.text(item, name=False)
            return (prev.start, prev.end, text, item) if text else None
        return None
    return None


def _as_label(doc: _Doc, index: int, before: tuple[int, int, str, int | None]) -> str:
    start, end, _, holder = before
    ident = doc.els[index].attrs["id"].strip()
    if holder is None:
        return f'<label for="{html.escape(ident, quote=True)}">{doc.source[start:end]}</label>'
    el = doc.els[holder]
    opening = doc.retag(holder, tag="label", first=(("for", ident),))
    return opening + doc.source[el.open_end:el.close_start] + "</label>"


def _field_tokens(el: _El) -> set[str]:
    keys = ("id", "name", "type", "autocomplete", "placeholder", "title", "inputmode")
    return _tokens(" ".join(el.attrs.get(key, "") for key in keys))


def _field_rule_tied(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    if goal.role not in FIELD_ROLES or goal.heard or not goal.name:
        return None
    found = [i for i, el in enumerate(doc.els) if _role(el) == goal.role and _unlabelled(doc, i)]
    for index in found:
        before = _text_before(doc, index)
        if before and doc.els[index].attrs.get("id", "").strip() and _same(before[2], goal.name):
            return _Edit(before[0], before[1], _as_label(doc, index, before),
                         f'rule 8: the {goal.role} "{_short(goal.name)}" had no label; the text "{_short(before[2])}" '
                         "right before it is now its label")
    if not found:
        return None
    want = _tokens(goal.name)
    best = min(found, key=lambda i: (-len(want & _field_tokens(doc.els[i])), i))
    el = doc.els[best]
    return _Edit(el.start, el.open_end, doc.retag(best, put={"aria-label": goal.name}),
                 f'rule 8: the unlabelled {goal.role} gets aria-label "{_short(goal.name)}"'
                 + (f" (1 of {len(found)} unlabelled fields)" if len(found) > 1 else ""))


def _field_rule_anywhere(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    """Without the expected name, only plain short text right before an unlabelled field can label it."""
    for index in range(len(doc.els)):
        if not _unlabelled(doc, index) or not doc.els[index].attrs.get("id", "").strip():
            continue
        before = _text_before(doc, index)
        if before and len(before[2]) <= 40 and not before[2].endswith(".") and not is_junk_name(before[2]):
            return _Edit(before[0], before[1], _as_label(doc, index, before),
                         f'rule 8: an unlabelled field had the text "{_short(before[2])}" right before it; '
                         f"that text is now its label{ELSEWHERE}")
    return None


# Rules 3, 4 and 6: a button or link with no name, or a name that says nothing.

def _name_problem(doc: _Doc, index: int) -> tuple[str, int | None] | None:
    """("alt", image) for a junk image alt, ("junk", None) for a junk aria-label on a control with no
    visible text, ("unnamed", None) for no name at all or one that says nothing; else None."""
    el = doc.els[index]
    if doc.labelledby(index) is not None:
        return None
    visible = doc.visible(index)
    label = el.attrs.get("aria-label", "").strip()
    if label:
        return ("junk", None) if is_junk_name(label) and not visible else None
    images = [index] if _is_image(el) else [i for i in doc.descendants(index) if _is_image(doc.els[i])]
    for image in images:
        alt = doc.els[image].attrs.get("alt", "").strip()
        if alt and is_junk_name(alt) and doc.rendered(image) and not doc.aria_hidden(image):
            return "alt", image
    if el.attrs.get("title", "").strip():
        return None
    content = doc.content_name(index)
    if not content or (not visible and is_junk_name(content)):
        return "unnamed", None
    return None


def _icon_only(doc: _Doc, index: int) -> bool:
    """A click-only element with no text counts as a control only when it holds an icon."""
    return any(doc.els[i].tag in ("svg", "img", "i") for i in doc.descendants(index))


def _control_tokens(doc: _Doc, index: int, *, submits: bool) -> set[str]:
    keys = ("id", "class", "name", "href", "src", "alt", "title", "onclick", "value")
    words = [doc.els[i].attrs.get(key, "") for i in [index, *doc.descendants(index)] for key in keys]
    form = doc.ancestor(index, "form")
    if submits and form is not None:
        words.append(doc.els[form].attrs.get("action", ""))
    return _tokens(" ".join(words))


def _naming_rule(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    if goal.role not in NAMED_ROLES or goal.heard or not goal.name:
        return None
    found: list[tuple[int, tuple[str, int | None], str]] = []
    for index, el in enumerate(doc.els):
        if not doc.rendered(index) or doc.aria_hidden(index):
            continue
        fake = _fake(doc, index)
        role = _role(el)
        if fake and not _explicit_role(el):
            if doc.visible(index) or not _icon_only(doc, index):
                continue
            role = goal.role  # a click-only icon can become either
        if role != goal.role:
            continue
        problem = _name_problem(doc, index)
        if problem is not None:
            found.append((index, problem, fake))
    if not found:
        return None
    want = _tokens(goal.name)

    def rank(item: tuple[int, tuple[str, int | None], str]) -> tuple:
        # The submit control first when the expected one submits; then words of the expected name
        # found in the control's own attributes (href="/checkout" for "Checkout"); then source order.
        index = item[0]
        submits = goal.submits and _is_submit(doc, index, expected_submit=True)
        return (goal.submits and not submits, -len(want & _control_tokens(doc, index, submits=submits)), index)

    index, (kind, image), fake = min(found, key=rank)
    el = doc.els[index]
    which = f" (1 of {len(found)} candidates)" if len(found) > 1 else ""
    submit = "submit " if goal.role == "button" and _is_submit(doc, index, expected_submit=goal.submits) else ""
    if fake:
        new, became = _convert(doc, index, goal.role, expected_submit=goal.submits, label=goal.name)
        return _Edit(el.start, el.end, new, f'rules 1 and 3: {fake} and has no name; it is now {became} '
                                           f'with aria-label "{_short(goal.name)}"{which}')
    if kind == "alt" and image is not None:
        img = doc.els[image]
        value = "" if doc.visible(index) else goal.name
        alt = _short(img.attrs.get("alt", ""))
        return _Edit(img.start, img.open_end, doc.retag(image, put={"alt": value}),
                     f'rule 4: the {submit}{goal.role} was named by the image alt "{alt}"; '
                     f'alt is now "{_short(value)}"{which}')
    new = doc.retag(index, put={"aria-label": goal.name})
    if kind == "junk":
        return _Edit(el.start, el.open_end, new, f'rule 6: the {submit}{goal.role} with aria-label '
                                                 f'"{_short(el.attrs.get("aria-label", ""))}" now has aria-label '
                                                 f'"{_short(goal.name)}"{which}')
    return _Edit(el.start, el.open_end, new,
                 f'rule 3: the unnamed {submit}{goal.role} gets aria-label "{_short(goal.name)}"{which}')


def _alt_anywhere(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    """Rule 4 without the expected name: a junk alt becomes the visible text heard on or next to it."""
    for index, el in enumerate(doc.els):
        if _role(el) not in NAMED_ROLES or not doc.rendered(index):
            continue
        problem = _name_problem(doc, index)
        if problem is None or problem[0] != "alt" or problem[1] is None:
            continue
        img = doc.els[problem[1]]
        alt = img.attrs.get("alt", "").strip()
        if doc.visible(index):
            value = ""
        else:
            value = next((" ".join(h.visible.split()) for h in result.heard[:MAX_HEARD]
                          if _fold(h.name) == _fold(alt) and h.visible.strip()), "") or _text_near(doc, index)
            if not value:
                continue
        return _Edit(img.start, img.open_end, doc.retag(problem[1], put={"alt": value}),
                     f'rule 4: an image alt "{_short(alt)}" named a {_role(el)}; '
                     f'alt is now "{_short(value)}"{ELSEWHERE}')
    return None


def _text_near(doc: _Doc, index: int) -> str:
    """Short plain text right before or after the element among its siblings, or ""."""
    el = doc.els[index]
    siblings = doc.els[el.parent].children if el.parent is not None else doc.top
    at = siblings.index(index)
    for side in (reversed(siblings[:at]), siblings[at + 1:]):
        for item in side:
            text = (" ".join(html.unescape(doc.source[item[0]:item[1]]).split()) if isinstance(item, tuple)
                    else doc.text(item, name=False) if doc.els[item].tag in TEXT_HOLDERS else "")
            if isinstance(item, tuple) and not text:
                continue
            if text and len(text) <= MAX_ATTR_TEXT and not is_junk_name(text):
                return text
            break
    return ""


# Rule 10 (extra): the expected heading is on the page but is not announced as a heading.

HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
NOT_INSIDE = HEADINGS | {"a", "button", "label", "legend", "option", "select", "summary"}


def _heading_rule(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    wanted = goal.heading
    if not wanted or any(h.role == "heading" and _fold(h.name) == _fold(wanted) for h in result.headings):
        return None
    for index, el in enumerate(doc.els):
        if not doc.rendered(index) or not (el.tag in HEADINGS or _explicit_role(el) == "heading"):
            continue
        if _attr_true(el, "aria-hidden") and _same(doc.text(index, name=False), wanted):
            return _Edit(el.start, el.open_end, doc.retag(index, drop={"aria-hidden"}),
                         f'rule 10 (extra): aria-hidden hid the heading "{_short(wanted)}" from screen readers; '
                         "removed it")
        problem = _name_problem(doc, index)
        if problem and problem[0] == "alt" and problem[1] is not None and not doc.visible(index):
            img = doc.els[problem[1]]
            return _Edit(img.start, img.open_end, doc.retag(problem[1], put={"alt": wanted}),
                         f'rule 10 (extra): the heading was an image with alt "{_short(img.attrs.get("alt", ""))}"; '
                         f'alt is now "{_short(wanted)}"')
    for index, el in enumerate(doc.els):
        if (el.tag not in TEXT_HOLDERS or _explicit_role(el) or not el.closed or el.end <= el.close_start
                or any(isinstance(child, int) for child in el.children) or not doc.rendered(index)
                or doc.aria_hidden(index)):
            continue
        outer = {doc.els[i].tag for i in doc.chain(index)[1:]}
        if outer & NOT_INSIDE or (el.tag not in ("div", "p") and "p" in outer):
            continue
        if _same(doc.text(index, name=False), wanted):
            level = "h2" if any(other.tag == "h1" for other in doc.els) else "h1"
            new = doc.retag(index, tag=level) + doc.source[el.open_end:el.close_start] + f"</{level}>"
            return _Edit(el.start, el.end, new, f'rule 10 (extra): "{_short(wanted)}" looked like a heading but was '
                                               f"a plain {el.tag}; it is now an <{level}>")
    return None


# The rules in order: first those tied to the expected control, then any barrier on the page.

def _tied_override(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    return _override_rule(doc, goal, result, tied=True)


def _any_override(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    return _override_rule(doc, goal, result, tied=False)


def _tied_labels(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    return _labels_rule(doc, goal, result, tied=True)


def _any_labels(doc: _Doc, goal: _Goal, result: Result) -> _Edit | None:
    return _labels_rule(doc, goal, result, tied=False)


RULES = (_native_tied, _tied_override, _tab_order, _tied_labels, _field_rule_tied, _naming_rule, _heading_rule,
         _native_anywhere, _any_override, _any_labels, _alt_anywhere, _field_rule_anywhere)


def propose_fix(journey: Journey, result: Result, template_path: str,
                template_source: str) -> tuple[Fix | None, str]:
    """One find/replace for the page template where the walk broke, and the rule that produced it.

    Returns (None, reason) when no rule applies. The find always occurs exactly once in
    template_source, and fix.file is template_path as given.
    """
    if result.clear or result.failed_step is None:
        return None, "no rule applies: the walk did not break"
    if not (template_source or "").strip():
        return None, "no rule applies: there is no template source to change"
    if len(template_source) > MAX_SOURCE_CHARS:
        return None, f"no rule applies: the template is longer than {MAX_SOURCE_CHARS} characters"
    try:
        doc = _Doc(template_source)
    except _TooLarge:
        return None, f"no rule applies: the template has more than {MAX_ELEMENTS} elements"
    goal = _goal(journey, result)
    for rule in RULES:
        edit = rule(doc, goal, result)
        if edit is None:
            continue
        fix = _make_fix(template_path, template_source, edit)
        if fix is not None:
            return fix, edit.reason
    expected = f'"{_short(goal.name)}, {goal.role}"' if goal.name else "the expected control"
    if goal.heading:
        expected = f'the heading "{_short(goal.heading)}", {expected}'
    page = template_path.rsplit("/", 1)[-1] or "the template"
    return None, (f"no rule applies: {page} has no click-only or fake control, unnamed or misnamed control, "
                  f"label problem or hidden heading, for {expected} or anywhere else")
