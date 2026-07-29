from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import tempfile
from typing import Any
import zipfile
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN_NS, "r": REL_NS, "p": PKG_REL_NS}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _column_index(cell_reference: str) -> int:
    match = re.match(r"([A-Z]+)", cell_reference)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_reference}")
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def _workbook_sheet_targets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships.findall("p:Relationship", NS)
    }
    resolved: list[tuple[str, str]] = []
    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        relationship_id = sheet.attrib[f"{{{REL_NS}}}id"]
        target = targets[relationship_id]
        if target.startswith("/"):
            target = target.lstrip("/")
        else:
            target = posixpath.normpath(posixpath.join("xl", target))
        resolved.append((sheet.attrib["name"], target))
    return resolved


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join((node.text or "") for node in item.findall(".//m:t", NS))
        for item in root.findall("m:si", NS)
    ]


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join((node.text or "") for node in cell.findall(".//m:t", NS))
    value = cell.find("m:v", NS)
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        return shared[int(value.text)]
    if cell_type == "b":
        return "true" if value.text == "1" else "false"
    return value.text


def workbook_sheet_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        return [name for name, _ in _workbook_sheet_targets(archive)]


def read_sheet_rows(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        targets = dict(_workbook_sheet_targets(archive))
        if sheet_name not in targets:
            raise KeyError(f"Sheet not found: {sheet_name}")
        root = ET.fromstring(archive.read(targets[sheet_name]))
        rows: list[list[str]] = []
        for row in root.findall("m:sheetData/m:row", NS):
            values: dict[int, str] = {}
            for cell in row.findall("m:c", NS):
                reference = cell.attrib.get("r", "")
                values[_column_index(reference)] = _cell_value(cell, shared)
            if values:
                width = max(values) + 1
                rows.append([values.get(index, "") for index in range(width)])
            else:
                rows.append([])
        return rows


def read_sheet_records(path: Path, sheet_name: str) -> list[dict[str, str]]:
    rows = read_sheet_rows(path, sheet_name)
    if not rows:
        return []
    headers = rows[0]
    records: list[dict[str, str]] = []
    for row in rows[2:]:
        padded = row + [""] * max(0, len(headers) - len(row))
        if not any(value not in ("", None) for value in padded):
            continue
        records.append({header: padded[index] for index, header in enumerate(headers)})
    return records


def read_headers(path: Path, sheet_name: str) -> list[str]:
    rows = read_sheet_rows(path, sheet_name)
    return rows[0] if rows else []


def parse_json_list(value: Any, field: str) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        parsed = value
    else:
        try:
            parsed = json.loads(str(value))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{field} must be a JSON array") from exc
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ValueError(f"{field} must be a JSON string array")
    return parsed


def replace_xlsx_tokens(path: Path, replacements: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "r") as source:
        with tempfile.NamedTemporaryFile(
            prefix=path.stem + "-", suffix=".xlsx", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
        try:
            with zipfile.ZipFile(temporary, "w") as target:
                for info in source.infolist():
                    data = source.read(info.filename)
                    if info.filename.endswith(".xml"):
                        try:
                            root = ET.fromstring(data)
                        except ET.ParseError:
                            pass
                        else:
                            changed = False
                            for element in root.iter():
                                if element.text:
                                    new_text = element.text
                                    for old, new in replacements.items():
                                        new_text = new_text.replace(old, new)
                                    if new_text != element.text:
                                        element.text = new_text
                                        changed = True
                            if changed:
                                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                    target.writestr(info, data)
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
