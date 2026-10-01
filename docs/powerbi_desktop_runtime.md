# Power BI Desktop Runtime Evidence Gate

Phase 9 converts the remaining Power BI blocker into a reproducible acceptance test.

## Why this gate exists

PBIR and TMDL can be structurally valid while still failing when Power BI Desktop loads or renders them.

Microsoft explicitly distinguishes external PBIR editing from Desktop runtime behavior. The repository therefore does not treat source-level validation as proof of rendered UX.

## Toolchain

Pinned runtime evidence uses:

- Power BI Desktop with Desktop Bridge enabled;
- `@microsoft/powerbi-desktop-bridge-cli@1.0.0`;
- `powerbi-desktop open`;
- `powerbi-desktop status`;
- `powerbi-desktop manifest`;
- `powerbi-desktop reload`;
- `powerbi-desktop screenshot-all`.

The static CI additionally uses the Microsoft PBIR authoring validator:

- `@microsoft/powerbi-report-authoring-cli@0.4.0`;
- `powerbi-report-author validate`.

Both npm versions are intentionally pinned because these tools are in preview.

## Runtime acceptance

The PowerShell harness rejects evidence unless:

1. the exact `HospitalityExecutive.pbip` project opens through Desktop Bridge;
2. the bridge reports `connected`;
3. the project resolves to exactly one target Desktop instance;
4. the runtime exposes the required reload and screenshot methods;
5. the report reload completes within the governed wait budget;
6. every page in PBIR `pages.json` is captured;
7. capture is complete, not partial;
8. four PNG screenshots are produced;
9. a content fingerprint binds the evidence to the current PBIP/PBIR/TMDL files.

The harness records `hasUnsavedChanges` only as an observation. Microsoft documents that some current Desktop builds report it as `true` immediately after opening an untouched PBIP, so that flag is not used as a pass/fail criterion for this owned validation instance.

## Run on Windows

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_powerbi_runtime_evidence.ps1 -InstallCli
```

The command writes public-safe evidence to:

```text
evidence/powerbi-desktop/
├── runtime_evidence.json
└── screenshots/
    └── *.png
```

Raw Bridge diagnostics stay under gitignored `output/powerbi-desktop/` because they can contain machine-local paths.

## After capture

Do not edit the Power BI project files after the capture.

Commit the evidence directory and let repository CI run:

```bash
python -m hospitality_intelligence.validate_desktop_evidence
```

The validator rejects stale evidence, screenshot tampering, incomplete page coverage, the wrong Bridge CLI version, missing required runtime methods, or a Power BI project fingerprint mismatch.

## Remaining review

A successful runtime capture proves Desktop opened and rendered every page.

It still does not automatically prove high-quality executive UX. The four screenshots must then receive an independent visual review for:

- clipping/overflow;
- unreadable labels;
- hierarchy;
- density;
- alignment;
- business narrative;
- color/contrast;
- decision usefulness.

Only after runtime evidence **and** screenshot review pass can the repository be reconsidered for OFFICIAL status.
