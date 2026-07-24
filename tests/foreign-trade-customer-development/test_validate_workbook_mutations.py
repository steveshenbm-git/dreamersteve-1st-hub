from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from openpyxl import load_workbook


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKBOOK_PATH = (
    REPO_ROOT
    / "plugins"
    / "foreign-trade-customer-development"
    / "skills"
    / "foreign-trade-customer-development"
    / "assets"
    / "prospect-development-workbook.xlsx"
)
VALIDATOR_PATH = Path(__file__).with_name("validate_workbook.py")


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def validation_by_range(sheet, expected_range: str):
    matches = [
        validation
        for validation in sheet.data_validations.dataValidation
        if str(validation.sqref) == expected_range
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected exactly one validation for {sheet.title}.{expected_range}, "
            f"observed {len(matches)}"
        )
    return matches[0]


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(path)],
        check=False,
        capture_output=True,
        text=True,
    )


def assert_rejected(result: subprocess.CompletedProcess[str], diagnostic: str) -> None:
    if result.returncode == 0:
        raise AssertionError(
            f"validator false-passed mutation {diagnostic!r}:\n{result.stdout}{result.stderr}"
        )
    combined = result.stdout + result.stderr
    if diagnostic not in combined:
        raise AssertionError(
            f"validator rejected mutation without named diagnostic {diagnostic!r}:\n{combined}"
        )


def main() -> int:
    source_hash = file_sha256(WORKBOOK_PATH)

    with TemporaryDirectory(prefix="ft-workbook-mutations-") as temp_dir:
        temp_root = Path(temp_dir)

        wrong_screening_path = temp_root / "wrong-screening-list.xlsx"
        workbook = load_workbook(WORKBOOK_PATH, data_only=False)
        validation = validation_by_range(workbook["客户总览"], "G3:G5000")
        validation.formula1 = '"待业务员筛选,已确认,NOT_A_VALID_SCREENING_STATE,已关闭"'
        workbook.save(wrong_screening_path)
        assert_rejected(
            run_validator(wrong_screening_path),
            "客户总览.screening_status",
        )

        disabled_risk_alert_path = temp_root / "disabled-risk-alert.xlsx"
        workbook = load_workbook(WORKBOOK_PATH, data_only=False)
        validation = validation_by_range(workbook["客户总览"], "J3:J5000")
        validation.showErrorMessage = False
        workbook.save(disabled_risk_alert_path)
        assert_rejected(
            run_validator(disabled_risk_alert_path),
            "客户总览.risk_gate: expected showErrorMessage=True",
        )

    if file_sha256(WORKBOOK_PATH) != source_hash:
        raise AssertionError("source workbook changed during mutation tests")

    print("PASS: validator rejects non-risk list and disabled risk-alert mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
