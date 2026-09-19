"""Load and validate a small provenance-backed evidence archive."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
DISPOSITIONS = {"active", "superseded", "record", "idea", "deferred"}


@dataclass(frozen=True, slots=True)
class Archive:
    records: tuple[dict[str, Any], ...]
    groups: tuple[dict[str, Any], ...]
    eras: tuple[dict[str, Any], ...]
    dispositions: dict[str, dict[str, Any]]
    verification: dict[str, int]

    def payload(self) -> dict[str, Any]:
        return {
            "records": list(self.records),
            "groups": list(self.groups),
            "eras": list(self.eras),
            "dispositions": self.dispositions,
            "verification": self.verification,
        }


def _read_json(path: Path, *, max_bytes: int = 2_000_000) -> Any:
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"Archive file exceeds {max_bytes} bytes: {path.name}")
    return json.loads(raw.decode("utf-8"))


def _read_jsonl(path: Path, *, max_bytes: int = 10_000_000) -> list[Any]:
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raise ValueError(f"Archive file exceeds {max_bytes} bytes: {path.name}")
    rows: list[Any] = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path.name}:{line_number}") from exc
    return rows


def _identifier(value: Any, label: str) -> str:
    result = str(value or "")
    if not IDENTIFIER.fullmatch(result):
        raise ValueError(f"Invalid {label}: {result!r}")
    return result


def _text(value: Any, label: str, *, maximum: int) -> str:
    result = str(value or "").strip()
    if not result or len(result) > maximum:
        raise ValueError(f"{label} must contain between 1 and {maximum} characters")
    return result


def _date(value: Any, label: str) -> str:
    result = str(value or "")
    try:
        date.fromisoformat(result)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date") from exc
    return result


def _source_path(value: Any) -> str:
    result = str(value or "")
    path = PurePosixPath(result)
    if not result or path.is_absolute() or ".." in path.parts or "\\" in result or ":" in result:
        raise ValueError(f"Source paths must be relative POSIX paths: {result!r}")
    return result


def load_archive(root: Path) -> Archive:
    root = root.resolve()
    records_raw = _read_jsonl(root / "records.jsonl")
    groups_raw = _read_json(root / "groups.json")
    eras_raw = _read_json(root / "eras.json")
    dispositions_raw = _read_json(root / "dispositions.json")
    if not isinstance(groups_raw, list) or not isinstance(eras_raw, list) or not isinstance(dispositions_raw, dict):
        raise ValueError("groups and eras must be arrays; dispositions must be an object")
    if len(records_raw) > 10_000 or len(groups_raw) > 1_000 or len(eras_raw) > 200:
        raise ValueError("Archive exceeds record, group, or era limits")

    records: list[dict[str, Any]] = []
    record_ids: set[str] = set()
    for index, raw in enumerate(records_raw, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Record {index} must be an object")
        record_id = _identifier(raw.get("id"), "record id")
        if record_id in record_ids:
            raise ValueError(f"Duplicate record id: {record_id}")
        record_ids.add(record_id)
        sources_raw = raw.get("sources")
        if not isinstance(sources_raw, list) or not sources_raw:
            raise ValueError(f"Record {record_id} must have at least one source")
        tags_raw = raw.get("tags", [])
        if not isinstance(tags_raw, list) or len(tags_raw) > 30:
            raise ValueError(f"Record {record_id} has invalid tags")
        records.append(
            {
                "id": record_id,
                "title": _text(raw.get("title"), "record title", maximum=200),
                "summary": _text(raw.get("summary"), "record summary", maximum=4_000),
                "date": _date(raw.get("date"), "record date"),
                "sources": [_source_path(value) for value in sources_raw],
                "tags": [_identifier(value, "tag") for value in tags_raw],
            }
        )

    groups: list[dict[str, Any]] = []
    group_ids: set[str] = set()
    for raw in groups_raw:
        if not isinstance(raw, dict):
            raise ValueError("Every group must be an object")
        group_id = _identifier(raw.get("id"), "group id")
        if group_id in group_ids:
            raise ValueError(f"Duplicate group id: {group_id}")
        group_ids.add(group_id)
        members = raw.get("record_ids", [])
        adjacent = raw.get("adjacent", [])
        if not isinstance(members, list) or not isinstance(adjacent, list):
            raise ValueError(f"Group {group_id} references must be arrays")
        groups.append(
            {
                "id": group_id,
                "title": _text(raw.get("title"), "group title", maximum=200),
                "narrative": _text(raw.get("narrative"), "group narrative", maximum=8_000),
                "record_ids": [_identifier(value, "record reference") for value in members],
                "adjacent": [_identifier(value, "adjacent group reference") for value in adjacent],
            }
        )

    for group in groups:
        missing_records = sorted(set(group["record_ids"]) - record_ids)
        missing_groups = sorted(set(group["adjacent"]) - group_ids)
        if missing_records:
            raise ValueError(f"Group {group['id']} references missing records: {missing_records}")
        if missing_groups:
            raise ValueError(f"Group {group['id']} references missing groups: {missing_groups}")
        if group["id"] in group["adjacent"]:
            raise ValueError(f"Group {group['id']} cannot be adjacent to itself")

    eras: list[dict[str, Any]] = []
    era_ids: set[str] = set()
    for raw in eras_raw:
        if not isinstance(raw, dict):
            raise ValueError("Every era must be an object")
        era_id = _identifier(raw.get("id"), "era id")
        if era_id in era_ids:
            raise ValueError(f"Duplicate era id: {era_id}")
        era_ids.add(era_id)
        era_groups = raw.get("group_ids", [])
        if not isinstance(era_groups, list):
            raise ValueError(f"Era {era_id} group_ids must be an array")
        start = _date(raw.get("start"), "era start")
        end = _date(raw.get("end"), "era end")
        if end < start:
            raise ValueError(f"Era {era_id} ends before it starts")
        normalized_groups = [_identifier(value, "era group reference") for value in era_groups]
        missing = sorted(set(normalized_groups) - group_ids)
        if missing:
            raise ValueError(f"Era {era_id} references missing groups: {missing}")
        eras.append(
            {
                "id": era_id,
                "title": _text(raw.get("title"), "era title", maximum=200),
                "summary": _text(raw.get("summary"), "era summary", maximum=4_000),
                "start": start,
                "end": end,
                "group_ids": normalized_groups,
            }
        )
    eras.sort(key=lambda item: (item["start"], item["id"]))

    dispositions: dict[str, dict[str, Any]] = {}
    for group_id, raw in dispositions_raw.items():
        group_id = _identifier(group_id, "disposition group id")
        if group_id not in group_ids or not isinstance(raw, dict):
            raise ValueError(f"Disposition references an unknown group: {group_id}")
        status = str(raw.get("status") or "").casefold()
        if status not in DISPOSITIONS:
            raise ValueError(f"Unsupported disposition for {group_id}: {status}")
        successor = str(raw.get("successor") or "")
        if successor and successor not in group_ids:
            raise ValueError(f"Disposition successor does not exist: {successor}")
        dispositions[group_id] = {
            "status": status,
            "successor": successor,
            "notes": str(raw.get("notes") or "")[:4_000],
        }

    source_count = sum(len(record["sources"]) for record in records)
    adjacency_count = sum(len(group["adjacent"]) for group in groups)
    return Archive(
        records=tuple(records),
        groups=tuple(groups),
        eras=tuple(eras),
        dispositions=dispositions,
        verification={
            "records": len(records),
            "records_with_sources": sum(1 for record in records if record["sources"]),
            "source_references": source_count,
            "groups": len(groups),
            "eras": len(eras),
            "adjacency_links": adjacency_count,
            "dispositions": len(dispositions),
        },
    )
