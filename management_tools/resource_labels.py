"""Shared machinery for the add_labels.py and del_labels.py tools.

Both tools edit ``meta.labels`` in genomic_resource.yaml files.  The edit is
done on the raw text -- only the lines of the label entries that actually
change are rewritten -- rather than by loading and re-dumping the document.
A full YAML round trip is not an option here: ruamel.yaml reformats 1097 of
the 2372 resources in this repository and fails to parse one of them, which
would bury a one-label change under a repository-wide reformat.

The document is parsed twice: ``yaml.safe_load`` for the current values and
``yaml.compose`` for the line marks of the nodes that have to be replaced.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml

RESOURCE_FILE_NAME = "genomic_resource.yaml"

#: Fallback indentation step, used when a block has to be created from
#: scratch and there is no sibling entry to copy the indentation from.
INDENT_STEP = 2

#: yaml.safe_dump folds long lines by default, which would turn a single
#: label into a multi-line entry.  Labels are short; keep them on one line.
_NO_WRAP = 10 ** 9

_NULL_TAG = "tag:yaml.org,2002:null"


class LabelEditError(Exception):
    """A resource definition cannot be edited safely."""


@dataclass
class Change:
    """One label of one resource, and what happened to it."""

    action: str  # added | updated | unchanged | removed | absent
    key: str
    old: Any = None
    new: Any = None

    #: Actions that mean the file on disk has to change.
    MODIFYING = frozenset({"added", "updated", "removed"})

    @property
    def modifies(self) -> bool:
        return self.action in self.MODIFYING

    def format(self) -> str:
        """One-line rendering for the tools' reports."""
        if self.action == "added":
            return f"+ {self.key}: {format_value(self.new)}"
        if self.action == "updated":
            return (f"~ {self.key}: {format_value(self.old)}"
                    f" -> {format_value(self.new)}")
        if self.action == "unchanged":
            return f"= {self.key}: {format_value(self.old)}"
        if self.action == "removed":
            return f"- {self.key}: {format_value(self.old)}"
        return f"? {self.key} (not present)"


def format_value(value: Any) -> str:
    """Render a label value for a report, on a single line."""
    dumped = yaml.safe_dump(
        value, default_flow_style=True, allow_unicode=True, width=_NO_WRAP)
    lines = dumped.rstrip("\n").split("\n")
    if lines and lines[-1] == "...":  # end-of-document marker after a scalar
        lines.pop()
    return " ".join(line.strip() for line in lines)


def find_resource_files(paths: Iterable[str | Path]) -> list[Path]:
    """Collect the genomic_resource.yaml files under the given paths.

    A path can be a directory -- searched recursively, skipping hidden
    subdirectories such as .git and .dvc -- or a genomic_resource.yaml file
    itself.  Duplicates coming from overlapping arguments are dropped.
    """
    found: list[Path] = []
    seen: set[Path] = set()
    for entry in paths:
        path = Path(entry)
        if path.is_file():
            if path.name != RESOURCE_FILE_NAME:
                raise LabelEditError(
                    f"{path}: not a {RESOURCE_FILE_NAME} file")
            candidates = [path]
        elif path.is_dir():
            candidates = [
                resource_file
                for resource_file in sorted(path.rglob(RESOURCE_FILE_NAME))
                if not any(part.startswith(".")
                           for part in resource_file.relative_to(path).parts)
            ]
        else:
            raise LabelEditError(f"{path}: no such file or directory")

        for resource_file in candidates:
            resolved = resource_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            found.append(resource_file)
    return found


def update_file(path: Path, *, add: dict[str, Any] | None = None,
                remove: Sequence[str] = (),
                dry_run: bool = False) -> tuple[list[Change], bool]:
    """Apply the label changes to one resource file.

    Returns the changes and whether the file's text had to change.  Nothing
    is written when ``dry_run`` is set, or when the labels already have the
    requested values.
    """
    text = path.read_text()
    try:
        new_text, changes = edit_labels(text, add=add, remove=remove)
    except LabelEditError as error:
        raise LabelEditError(f"{path}: {error}") from error
    changed = new_text != text
    if changed and not dry_run:
        path.write_text(new_text)
    return changes, changed


def edit_labels(text: str, *, add: dict[str, Any] | None = None,
                remove: Sequence[str] = ()) -> tuple[str, list[Change]]:
    """Return the resource definition with its ``meta.labels`` updated."""
    add = dict(add or {})
    document = yaml.safe_load(text)
    if document is not None and not isinstance(document, dict):
        raise LabelEditError("the resource definition is not a YAML mapping")

    current = _current_labels(document)
    labels = dict(current)
    changes: list[Change] = []
    for key, value in add.items():
        if key not in labels:
            changes.append(Change("added", key, new=value))
        elif labels[key] != value:
            changes.append(Change("updated", key, old=labels[key], new=value))
        else:
            changes.append(Change("unchanged", key, old=value))
        labels[key] = value
    for key in remove:
        if key in labels:
            changes.append(Change("removed", key, old=labels.pop(key)))
        else:
            changes.append(Change("absent", key))

    if labels == current:
        return text, changes

    if text and not text.endswith("\n"):
        text += "\n"
    new_text = _write_labels(text, labels)
    _verify(text, new_text, labels)
    return new_text, changes


def _current_labels(document: dict | None) -> dict[str, Any]:
    meta = document.get("meta") if isinstance(document, dict) else None
    labels = meta.get("labels") if isinstance(meta, dict) else None
    if labels is None:
        return {}
    if not isinstance(labels, dict):
        raise LabelEditError(
            f"meta.labels is a {type(labels).__name__}, not a mapping")
    return labels


# --- placing the new labels into the raw text ------------------------------


def _write_labels(text: str, labels: dict[str, Any]) -> str:
    """Rewrite the smallest region of ``text`` that holds ``meta.labels``."""
    lines = text.splitlines(keepends=True)
    root = yaml.compose(text)

    meta_key = meta_value = None
    if root is not None:
        meta_key, meta_value = _find_entry(root, "meta")

    # No `meta` at all, or `meta:` with nothing under it: (re)create the
    # whole section.  Root keys sit at column 0 in every resource here, but
    # take the column from the document when there is one.
    if meta_key is None:
        indent = _first_key_column(root, default=0)
        block = _render_block("meta", _render_labels(labels, indent + 2 * INDENT_STEP),
                              indent, "labels", indent + INDENT_STEP)
        return "".join(lines) + block
    if not _is_block_mapping(meta_value):
        indent = meta_key.start_mark.column
        block = _render_block("meta", _render_labels(labels, indent + 2 * INDENT_STEP),
                              indent, "labels", indent + INDENT_STEP)
        return _splice(lines, [(meta_key.start_mark.line,
                                _value_end_line(lines, meta_key, meta_value),
                                block)])

    meta_indent = meta_value.value[0][0].start_mark.column
    labels_key, labels_value = _find_entry(meta_value, "labels")

    # `meta` is there but carries no labels: append a labels block to it.
    if labels_key is None:
        meta_end = _block_extent(
            lines, meta_value.value[0][0].start_mark.line, meta_indent)
        entries = _render_labels(labels, meta_indent + INDENT_STEP)
        return _splice(lines, [(meta_end, meta_end,
                                f"{' ' * meta_indent}labels:\n{entries}")])

    # `labels: ~`, `labels: {}` or a flow mapping: replace it wholesale.
    if not _is_block_mapping(labels_value):
        entries = _render_labels(labels, meta_indent + INDENT_STEP)
        replacement = f"{' ' * meta_indent}labels:\n{entries}" if labels else ""
        return _splice(lines, [(labels_key.start_mark.line,
                                _value_end_line(lines, labels_key, labels_value),
                                replacement)])

    # A block mapping: touch only the entries that changed.
    entry_indent = labels_value.value[0][0].start_mark.column
    block_start = labels_value.value[0][0].start_mark.line
    block_end = _block_extent(lines, block_start, entry_indent)

    if not labels:  # every label was deleted -- drop the key as well
        return _splice(lines,
                       [(labels_key.start_mark.line, block_end, "")])

    spans = _entry_spans(lines, labels_value, block_end,
                         labels_key.start_mark.line + 1)
    edits: list[tuple[int, int, str]] = []
    for key, (start, end, delete_start) in spans.items():
        if key not in labels:
            # Deleting takes the entry's own comments with it; rewriting a
            # value leaves them where the curator put them.
            edits.append((delete_start, end, ""))
        elif labels[key] != _entry_text_value(lines, start, end, key):
            edits.append((start, end, _render_entry(key, labels[key], entry_indent)))
    appended = "".join(_render_entry(key, value, entry_indent)
                       for key, value in labels.items() if key not in spans)
    if appended:
        edits.append((block_end, block_end, appended))
    return _splice(lines, edits)


def _entry_text_value(lines: list[str], start: int, end: int, key: str) -> Any:
    """The value currently written on the entry's own lines.

    Used to leave an entry byte-identical when its value is unchanged, even
    if the same key appears twice in the block.
    """
    entry = "".join(lines[start:end])
    dedented = "".join(line[min(_indent_of(line), _indent_of(lines[start])):]
                       if line.strip() else line
                       for line in entry.splitlines(keepends=True))
    try:
        return (yaml.safe_load(dedented) or {}).get(key)
    except yaml.YAMLError:
        return object()  # unparsable on its own: force a rewrite


def _render_labels(labels: dict[str, Any], indent: int) -> str:
    return "".join(_render_entry(key, value, indent)
                   for key, value in labels.items())


def _render_entry(key: str, value: Any, indent: int) -> str:
    entry = yaml.safe_dump({key: value}, default_flow_style=False,
                           sort_keys=False, allow_unicode=True, width=_NO_WRAP)
    pad = " " * indent
    return "".join(pad + line if line.strip() else line
                   for line in entry.splitlines(keepends=True))


def _render_block(outer_key: str, entries: str, outer_indent: int,
                  inner_key: str, inner_indent: int) -> str:
    return (f"{' ' * outer_indent}{outer_key}:\n"
            f"{' ' * inner_indent}{inner_key}:\n{entries}")


def _splice(lines: list[str], edits: list[tuple[int, int, str]]) -> str:
    """Apply (start, end, replacement) line edits, last one first."""
    for start, end, replacement in sorted(edits, key=lambda e: e[0],
                                          reverse=True):
        lines[start:end] = [replacement] if replacement else []
    return "".join(lines)


# --- reading the parse tree ------------------------------------------------


def _find_entry(mapping: yaml.Node,
                key: str) -> tuple[yaml.Node | None, yaml.Node | None]:
    if not isinstance(mapping, yaml.MappingNode):
        return None, None
    for key_node, value_node in mapping.value:
        if isinstance(key_node, yaml.ScalarNode) and key_node.value == key:
            return key_node, value_node
    return None, None


def _is_block_mapping(node: yaml.Node | None) -> bool:
    return (isinstance(node, yaml.MappingNode)
            and not node.flow_style and bool(node.value))


def _first_key_column(root: yaml.Node | None, default: int) -> int:
    if isinstance(root, yaml.MappingNode) and root.value:
        return root.value[0][0].start_mark.column
    return default


def _value_end_line(lines: list[str], key_node: yaml.Node,
                    value_node: yaml.Node | None) -> int:
    """One past the last line covered by an entry's key and value."""
    end = key_node.start_mark.line + 1
    if value_node is not None:
        value_end = value_node.end_mark.line
        if value_node.end_mark.column > 0:
            value_end += 1
        end = max(end, value_end)
    return min(end, len(lines))


def _block_extent(lines: list[str], start: int, indent: int) -> int:
    """One past the last line of the block whose entries start at ``indent``.

    Blank lines and comments inside the block are kept; trailing ones are
    left to whatever follows the block.
    """
    end = index = start
    while index < len(lines):
        line = lines[index]
        if _is_blank(line) or _is_comment(line):
            index += 1
            continue
        if _indent_of(line) < indent:
            break
        index += 1
        end = index
    return end


def _entry_spans(lines: list[str], mapping: yaml.MappingNode, block_end: int,
                 block_start: int) -> dict[str, tuple[int, int, int]]:
    """The line spans of the entries of a block mapping.

    Each entry gets ``(start, end, delete_start)``: the lines the entry
    itself occupies, and the earlier line a deletion should start from so
    that the comment block written directly above the key goes with it.
    """
    starts = [key_node.start_mark.line for key_node, _ in mapping.value]
    spans: dict[str, tuple[int, int, int]] = {}
    previous_end = block_start
    for position, (key_node, _) in enumerate(mapping.value):
        start = starts[position]
        end = starts[position + 1] if position + 1 < len(starts) else block_end
        # A comment right above the next key documents that key, so leave
        # trailing blanks and comments out of this entry's span.
        while end > start + 1 and (_is_blank(lines[end - 1])
                                   or _is_comment(lines[end - 1])):
            end -= 1
        delete_start = start
        while delete_start > previous_end and _is_comment(lines[delete_start - 1]):
            delete_start -= 1
        spans[key_node.value] = (start, end, delete_start)
        previous_end = end
    return spans


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip())


def _is_blank(line: str) -> bool:
    return not line.strip()


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


# --- safety net ------------------------------------------------------------


def _verify(old_text: str, new_text: str, expected: dict[str, Any]) -> None:
    """Check that the edit changed ``meta.labels`` and nothing else."""
    try:
        new_document = yaml.safe_load(new_text)
    except yaml.YAMLError as error:
        raise LabelEditError(
            f"the edit would produce an invalid YAML file: {error}") from error

    written = _current_labels(new_document)
    if written != expected:
        raise LabelEditError(
            f"the edit produced labels {written!r} instead of {expected!r}")
    if _without_labels(yaml.safe_load(old_text)) != _without_labels(new_document):
        raise LabelEditError(
            "the edit would change the resource definition outside meta.labels")


def _without_labels(document: Any) -> Any:
    if not isinstance(document, dict):
        return document
    stripped = dict(document)
    meta = stripped.get("meta")
    if isinstance(meta, dict):
        meta = {key: value for key, value in meta.items() if key != "labels"}
    # An absent `meta`, `meta: ~` and a `meta` holding nothing but labels all
    # describe the same document once the labels are taken out.
    if meta:
        stripped["meta"] = meta
    else:
        stripped.pop("meta", None)
    return stripped
