from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Iterable


SECTION_ORDER = ("Backlog", "In Progress", "Blocked", "Done")


@dataclass(slots=True)
class KanbanItem:
    id: str
    title: str
    assignee: str
    priority: str
    notes: str = ""


@dataclass(slots=True)
class KanbanSection:
    name: str
    items: list[KanbanItem] = field(default_factory=list)


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_kanban_markdown(path: Path) -> list[KanbanSection]:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: list[KanbanSection] = []
    current: KanbanSection | None = None
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            section_name = line.removeprefix("## ").strip()
            if section_name in SECTION_ORDER:
                current = KanbanSection(name=section_name)
                sections.append(current)
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("|"):
                    i += 1
                if i >= len(lines):
                    break
                i += 1  # skip header row
                if i < len(lines) and set(lines[i].strip()) <= {"|", "-", " "}:
                    i += 1
                while i < len(lines):
                    row = lines[i].strip()
                    if not row:
                        break
                    if row.startswith("## "):
                        i -= 1
                        break
                    if row.startswith("|"):
                        cells = _split_row(row)
                        if len(cells) >= 5 and cells[0] != "ID":
                            current.items.append(
                                KanbanItem(
                                    id=cells[0],
                                    title=cells[1],
                                    assignee=cells[2],
                                    priority=cells[3],
                                    notes=cells[5] if len(cells) > 5 else "",
                                )
                            )
                    i += 1
        i += 1

    return sections


def sections_to_html(sections: Iterable[KanbanSection]) -> str:
    chunks: list[str] = []
    for section in sections:
        rows = [
            "<tr><th>ID</th><th>Title</th><th>Assignee</th><th>Priority</th><th>Notes</th></tr>"
        ]
        for item in section.items:
            rows.append(
                "<tr>"
                f"<td>{escape(item.id)}</td>"
                f"<td>{escape(item.title)}</td>"
                f"<td>{escape(item.assignee)}</td>"
                f"<td>{escape(item.priority)}</td>"
                f"<td>{escape(item.notes)}</td>"
                "</tr>"
            )
        chunks.append(
            f"<section class='panel'><h2>{escape(section.name)}</h2><table>{''.join(rows)}</table></section>"
        )
    return "".join(chunks)
