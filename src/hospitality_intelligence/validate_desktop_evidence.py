"""Validate committed Power BI Desktop runtime evidence without trusting filenames alone."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE = ROOT / "evidence" / "powerbi-desktop" / "runtime_evidence.json"
PAGES_PATH = (
    ROOT
    / "powerbi"
    / "HospitalityExecutive.Report"
    / "definition"
    / "pages"
    / "pages.json"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def powerbi_fingerprint(root: Path = ROOT) -> str:
    """Fingerprint the tracked Power BI project files used by Desktop evidence."""

    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "powerbi/HospitalityExecutive.pbip",
            "powerbi/HospitalityExecutive.Report/**",
            "powerbi/HospitalityExecutive.SemanticModel/**",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    paths = sorted(line.strip() for line in result.stdout.splitlines() if line.strip())
    if not paths:
        raise ValueError("No tracked Power BI project files found")

    rows: list[str] = []
    for relative in paths:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"Tracked Power BI file is missing: {relative}")
        rows.append(f"{relative.replace(chr(92), '/')}:{_sha256(path)}")

    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def expected_pages() -> list[str]:
    payload = json.loads(PAGES_PATH.read_text(encoding="utf-8-sig"))
    pages = payload.get("pageOrder")
    if not isinstance(pages, list) or not pages:
        raise ValueError("PBIR page order is missing")
    return [str(page) for page in pages]


def validate_runtime_evidence(
    evidence_path: Path = DEFAULT_EVIDENCE,
    *,
    allow_missing: bool = False,
) -> list[str]:
    """Return evidence errors; optionally treat missing evidence as pending."""

    if not evidence_path.exists():
        return [] if allow_missing else ["Power BI Desktop runtime evidence is missing"]

    evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []

    if evidence.get("status") != "PASS":
        errors.append("runtime evidence status must be PASS")
    if evidence.get("powerBiFingerprint") != powerbi_fingerprint():
        errors.append("runtime evidence does not match the current Power BI project fingerprint")

    checks = evidence.get("checks")
    if not isinstance(checks, dict):
        errors.append("runtime evidence checks are missing")
    else:
        required_checks = {
            "bridgeConnected": True,
            "instanceResolvedUniquely": True,
            "reloadCompleted": True,
            "allPagesCaptured": True,
        }
        for key, expected in required_checks.items():
            if checks.get(key) is not expected:
                errors.append(f"runtime check {key} must equal {expected}")

    expected = expected_pages()
    page_order = evidence.get("pageOrder")
    if page_order != expected:
        errors.append("runtime evidence page order does not match PBIR pages.json")

    screenshots = evidence.get("screenshots")
    if not isinstance(screenshots, list):
        errors.append("runtime screenshot evidence is missing")
        screenshots = []

    by_page: dict[str, dict[str, object]] = {}
    for row in screenshots:
        if not isinstance(row, dict):
            errors.append("screenshot evidence row must be an object")
            continue
        page_id = str(row.get("pageId", ""))
        if page_id in by_page:
            errors.append(f"duplicate screenshot evidence for page {page_id}")
        by_page[page_id] = row

        relative = str(row.get("file", ""))
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing screenshot file for page {page_id}: {relative}")
            continue
        if path.suffix.lower() != ".png":
            errors.append(f"screenshot for page {page_id} must be PNG")
            continue
        with path.open("rb") as handle:
            if handle.read(8) != b"\x89PNG\r\n\x1a\n":
                errors.append(f"screenshot for page {page_id} is not a valid PNG signature")
        if row.get("sha256") != _sha256(path):
            errors.append(f"screenshot hash mismatch for page {page_id}")

    if set(by_page) != set(expected):
        errors.append(
            f"screenshot page coverage mismatch: expected={sorted(expected)} "
            f"observed={sorted(by_page)}"
        )

    if evidence.get("pageCount") != len(expected):
        errors.append("runtime evidence pageCount does not match PBIR")

    if not evidence.get("powerBiDesktopVersion"):
        errors.append("Power BI Desktop version is missing")
    if evidence.get("desktopBridgeCliVersion") != "1.0.0":
        errors.append("Desktop Bridge CLI evidence must come from pinned version 1.0.0")

    methods = set(evidence.get("bridgeMethods") or [])
    required_methods = {
        "application.state.get/v1",
        "report.snapshot.capture/v1",
        "file.reload/v1",
    }
    if not required_methods.issubset(methods):
        errors.append(
            "Desktop Bridge manifest is missing required methods: "
            f"{sorted(required_methods - methods)}"
        )

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Power BI Desktop runtime evidence.")
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--allow-missing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors = validate_runtime_evidence(args.evidence, allow_missing=args.allow_missing)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)

    if args.allow_missing and not args.evidence.exists():
        print("Power BI Desktop runtime evidence: PENDING")
    else:
        print("Power BI Desktop runtime evidence: PASS")


if __name__ == "__main__":
    main()
