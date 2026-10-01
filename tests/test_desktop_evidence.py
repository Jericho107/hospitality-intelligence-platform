import hashlib
import json
from pathlib import Path

import hospitality_intelligence.validate_desktop_evidence as module
from hospitality_intelligence.validate_desktop_evidence import (
    expected_pages,
    powerbi_fingerprint,
    validate_runtime_evidence,
)


PNG = b"\x89PNG\r\n\x1a\n" + b"synthetic-png-fixture"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_missing_runtime_evidence_can_remain_pending(tmp_path: Path) -> None:
    missing = tmp_path / "runtime_evidence.json"
    assert validate_runtime_evidence(missing, allow_missing=True) == []
    assert validate_runtime_evidence(missing, allow_missing=False)


def test_powerbi_fingerprint_is_stable() -> None:
    assert powerbi_fingerprint() == powerbi_fingerprint()
    assert len(powerbi_fingerprint()) == 64


def test_expected_runtime_page_contract_is_four_pages() -> None:
    assert expected_pages() == [
        "executive_overview",
        "rooms_performance",
        "fnb_inventory",
        "procurement_labour",
    ]


def test_tampered_screenshot_is_rejected(tmp_path: Path, monkeypatch) -> None:
    evidence_dir = tmp_path / "evidence" / "powerbi-desktop"
    screenshot_dir = evidence_dir / "screenshots"
    screenshot_dir.mkdir(parents=True)

    screenshots = []
    for page in expected_pages():
        path = screenshot_dir / f"{page}.png"
        path.write_bytes(PNG)
        screenshots.append(
            {
                "pageId": page,
                "displayName": page,
                "file": str(path.relative_to(tmp_path)).replace("\\", "/"),
                "sha256": _sha(PNG),
            }
        )

    evidence = {
        "schemaVersion": 1,
        "status": "PASS",
        "powerBiFingerprint": "fixture-fingerprint",
        "powerBiDesktopVersion": "2.0.0",
        "desktopBridgeCliVersion": "1.0.0",
        "bridgeMethods": [
            "application.state.get/v1",
            "report.snapshot.capture/v1",
            "file.reload/v1",
        ],
        "pageCount": 4,
        "pageOrder": expected_pages(),
        "checks": {
            "bridgeConnected": True,
            "unsavedChanges": False,
            "reloadCompleted": True,
            "allPagesCaptured": True,
        },
        "screenshots": screenshots,
    }
    evidence_path = evidence_dir / "runtime_evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "powerbi_fingerprint", lambda root=tmp_path: "fixture-fingerprint")

    assert validate_runtime_evidence(evidence_path) == []

    first = tmp_path / screenshots[0]["file"]
    first.write_bytes(PNG + b"tampered")
    errors = validate_runtime_evidence(evidence_path)
    assert any("hash mismatch" in error for error in errors)
