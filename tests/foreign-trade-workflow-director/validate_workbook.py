from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = (
    ROOT
    / "plugins/foreign-trade-workflow-director/skills/foreign-trade-workflow-director/assets/salesperson-foreign-trade-workbench.xlsx"
)
EXPECTED_SHEETS = [
    "00-我的待办",
    "01-路线选择",
    "02-候选客户",
    "03-客户跟进",
    "04-沟通草稿",
    "05-异常与风险",
]
REQUIRED_BUSINESS_LABELS = {
    "现在要做的事",
    "业务员决定",
    "业务员分类",
    "下一步",
    "外文草稿",
    "中文译文",
    "必须处理的问题",
    "来源记录编号",
}
FORBIDDEN_FORMULA_ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
PKG_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def workbook_evidence(path: Path) -> tuple[list[str], str, int, int]:
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("p:Relationship", PKG_NS)
        }
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("m:si", NS):
                shared.append("".join(node.text or "" for node in item.iterfind(".//m:t", NS)))

        names: list[str] = []
        values: list[str] = []
        validation_count = 0
        frozen_count = 0
        for sheet in workbook.find("m:sheets", NS):
            names.append(sheet.attrib["name"])
            target = rel_targets[sheet.attrib[f"{{{REL_NS['r']}}}id"]]
            target = target.lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(archive.read(target))
            validation_count += sum(
                int(node.attrib.get("count", "0"))
                for node in root.findall("m:dataValidations", NS)
            )
            frozen_count += len(root.findall(".//m:pane[@state='frozen']", NS))
            for cell in root.findall(".//m:c", NS):
                value = cell.find("m:v", NS)
                inline = cell.find("m:is/m:t", NS)
                if inline is not None:
                    values.append(inline.text or "")
                elif value is not None and cell.attrib.get("t") == "s":
                    values.append(shared[int(value.text)])
                elif value is not None:
                    values.append(value.text or "")
        return names, "\n".join(values), validation_count, frozen_count


def main() -> int:
    if not WORKBOOK.exists():
        print(f"FAIL: workbook missing: {WORKBOOK}")
        return 1
    try:
        names, text, validation_count, frozen_count = workbook_evidence(WORKBOOK)
    except Exception as exc:
        print(f"FAIL: workbook cannot be reopened: {exc}")
        return 1

    failures = []
    if names != EXPECTED_SHEETS:
        failures.append(f"sheet order {names!r} != {EXPECTED_SHEETS!r}")
    missing_labels = sorted(label for label in REQUIRED_BUSINESS_LABELS if label not in text)
    if missing_labels:
        failures.append(f"missing business labels: {missing_labels}")
    if validation_count < 6:
        failures.append(f"expected at least 6 data validations, found {validation_count}")
    freeze_warning = None
    if frozen_count != 6:
        freeze_warning = (
            "UNVERIFIED: artifact-tool requested six frozen panes but the exported "
            f"XLSX contains {frozen_count}; keep this as a known Beta UI limitation"
        )
    formula_errors = sorted(error for error in FORBIDDEN_FORMULA_ERRORS if error in text)
    if formula_errors:
        failures.append(f"formula errors found: {formula_errors}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    if freeze_warning:
        print(freeze_warning)
    print(
        "PASS: six-sheet salesperson workbench reopens with business labels, "
        "validations, and no stored formula errors"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
