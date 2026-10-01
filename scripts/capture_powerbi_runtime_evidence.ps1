[CmdletBinding()]
param(
    [switch]$InstallCli,
    [int]$DesktopProcessId = 0,
    [int]$Scale = 2
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ProjectPath = Join-Path $RepoRoot "powerbi\HospitalityExecutive.pbip"
$ReportDir = Join-Path $RepoRoot "powerbi\HospitalityExecutive.Report"
$PagesPath = Join-Path $ReportDir "definition\pages\pages.json"
$EvidenceDir = Join-Path $RepoRoot "evidence\powerbi-desktop"
$ScreenshotDir = Join-Path $EvidenceDir "screenshots"
$LocalOutputDir = Join-Path $RepoRoot "output\powerbi-desktop"

function Require-Command {
    param([string]$Name, [string]$Hint)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing command '$Name'. $Hint"
    }
}

function Invoke-BridgeJson {
    param(
        [string[]]$Arguments,
        [string]$DiagnosticName
    )

    $stderrPath = Join-Path $LocalOutputDir "$DiagnosticName.stderr.txt"
    $stdout = & powerbi-desktop @Arguments 2> $stderrPath
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        $stderr = if (Test-Path $stderrPath) { Get-Content $stderrPath -Raw } else { "" }
        throw "powerbi-desktop $($Arguments -join ' ') failed with exit code $exitCode. $stderr"
    }

    $raw = ($stdout -join [Environment]::NewLine).Trim()
    if (-not $raw) {
        throw "powerbi-desktop $($Arguments -join ' ') returned no JSON output."
    }
    try {
        return $raw | ConvertFrom-Json -Depth 50
    }
    catch {
        throw "Could not parse JSON from powerbi-desktop $($Arguments -join ' ')."
    }
}

function Get-Payload {
    param($Object)
    if ($null -ne $Object.data) { return $Object.data }
    return $Object
}

function Get-Sha256 {
    param([string]$Path)
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Get-PowerBiFingerprint {
    param([string]$Root)

    $tracked = & git -C $Root ls-files "powerbi/HospitalityExecutive.pbip" "powerbi/HospitalityExecutive.Report/**" "powerbi/HospitalityExecutive.SemanticModel/**"
    if ($LASTEXITCODE -ne 0 -or -not $tracked) {
        throw "Could not enumerate tracked Power BI files."
    }

    $lines = foreach ($relative in ($tracked | Sort-Object)) {
        $full = Join-Path $Root $relative
        if (-not (Test-Path $full -PathType Leaf)) {
            throw "Tracked Power BI file is missing: $relative"
        }
        "$($relative.Replace('\','/')):$((Get-Sha256 $full))"
    }

    $payload = [Text.Encoding]::UTF8.GetBytes(($lines -join [Environment]::NewLine))
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash($payload))).Replace("-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

if ($Scale -lt 1 -or $Scale -gt 3) {
    throw "Scale must be between 1 and 3."
}

Require-Command "git" "Install Git and ensure it is available on PATH."
Require-Command "npm" "Install Node.js/npm before running the Desktop evidence gate."

if (-not (Get-Command "powerbi-desktop" -ErrorAction SilentlyContinue)) {
    if (-not $InstallCli) {
        throw "Power BI Desktop Bridge CLI is missing. Re-run with -InstallCli or install @microsoft/powerbi-desktop-bridge-cli@1.0.0 globally."
    }
    npm install -g @microsoft/powerbi-desktop-bridge-cli@1.0.0
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install @microsoft/powerbi-desktop-bridge-cli@1.0.0."
    }
}

Require-Command "powerbi-desktop" "Desktop Bridge CLI installation failed."

$installedInfoRaw = npm list -g @microsoft/powerbi-desktop-bridge-cli --json
$installedInfo = $installedInfoRaw | ConvertFrom-Json -Depth 20
$installedCliVersion = [string]$installedInfo.dependencies.'@microsoft/powerbi-desktop-bridge-cli'.version
if ($installedCliVersion -ne "1.0.0") {
    if ($InstallCli) {
        npm install -g @microsoft/powerbi-desktop-bridge-cli@1.0.0
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to pin @microsoft/powerbi-desktop-bridge-cli@1.0.0."
        }
        $installedCliVersion = "1.0.0"
    }
    else {
        throw "Desktop Bridge CLI version $installedCliVersion is installed; Phase 9 requires pinned version 1.0.0. Re-run with -InstallCli."
    }
}

if (-not (Test-Path $ProjectPath -PathType Leaf)) {
    throw "Missing PBIP project shortcut: $ProjectPath"
}
if (-not (Test-Path $PagesPath -PathType Leaf)) {
    throw "Missing PBIR pages metadata: $PagesPath"
}

New-Item -ItemType Directory -Force -Path $LocalOutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
if (Test-Path $ScreenshotDir) {
    Remove-Item $ScreenshotDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $ScreenshotDir | Out-Null

# Launch the governed project and let the CLI wait for the bridge.
$open = Invoke-BridgeJson -Arguments @("open", $ProjectPath) -DiagnosticName "open"
$open | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $LocalOutputDir "open.json") -Encoding utf8

$status = Get-Payload (Invoke-BridgeJson -Arguments @("status") -DiagnosticName "status")
$status | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $LocalOutputDir "status.json") -Encoding utf8

$instances = @($status.instances)
if ($instances.Count -eq 0) {
    throw "No Power BI Desktop Bridge instance is available after opening the project."
}

if ($DesktopProcessId -gt 0) {
    $matches = @($instances | Where-Object { [int]$_.pid -eq $DesktopProcessId })
}
else {
    $expected = [IO.Path]::GetFullPath($ProjectPath)
    $matches = @(
        $instances | Where-Object {
            $_.currentFilePath -and
            ([IO.Path]::GetFullPath([string]$_.currentFilePath) -eq $expected)
        }
    )
}

if ($matches.Count -ne 1) {
    throw "Expected exactly one Desktop instance for HospitalityExecutive.pbip; found $($matches.Count). Use -DesktopProcessId when several Desktop windows are open."
}

$instance = $matches[0]
$pidValue = [int]$instance.pid

if ([string]$instance.bridgeStatus -ne "connected") {
    throw "Desktop Bridge is not connected for PID $pidValue."
}
if ([bool]$instance.hasUnsavedChanges) {
    throw "Power BI Desktop has unsaved changes. Save or discard them before runtime validation."
}

$manifest = Get-Payload (Invoke-BridgeJson -Arguments @("manifest", "--pid", "$pidValue") -DiagnosticName "manifest")
$manifest | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $LocalOutputDir "manifest.json") -Encoding utf8

$reload = Get-Payload (Invoke-BridgeJson -Arguments @("reload", "--pid", "$pidValue") -DiagnosticName "reload")
$reload | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $LocalOutputDir "reload.json") -Encoding utf8

$capture = Get-Payload (Invoke-BridgeJson -Arguments @(
    "screenshot-all",
    "--pid", "$pidValue",
    "--output-dir", $ScreenshotDir,
    "--scale", "$Scale"
) -DiagnosticName "screenshot-all")
$capture | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $LocalOutputDir "screenshot-all.json") -Encoding utf8

if ($capture.ok -eq $false) {
    throw "Desktop screenshot capture failed."
}
if ([string]$capture.status -eq "partial") {
    throw "Desktop screenshot capture was partial; runtime evidence is rejected."
}
if (@($capture.failures).Count -gt 0) {
    throw "Desktop screenshot capture contains page failures."
}

$pages = Get-Content $PagesPath -Raw | ConvertFrom-Json
$expectedPageIds = @($pages.pageOrder)
$captures = @($capture.captures)
if ($captures.Count -ne $expectedPageIds.Count) {
    throw "Expected $($expectedPageIds.Count) screenshots; received $($captures.Count)."
}

$capturedIds = @($captures | ForEach-Object { [string]$_.pageId })
$missingIds = @($expectedPageIds | Where-Object { $_ -notin $capturedIds })
if ($missingIds.Count -gt 0) {
    throw "Missing screenshots for PBIR pages: $($missingIds -join ', ')"
}

$screenshotEvidence = foreach ($row in $captures) {
    $path = [string]$row.path
    if (-not $path) {
        throw "Capture result for page $($row.pageId) does not expose an output path."
    }
    $resolved = (Resolve-Path $path).Path
    if (-not $resolved.StartsWith((Resolve-Path $ScreenshotDir).Path, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Screenshot was written outside the governed evidence directory: $resolved"
    }
    $relative = [IO.Path]::GetRelativePath($RepoRoot, $resolved).Replace("\", "/")
    [ordered]@{
        pageId = [string]$row.pageId
        displayName = [string]$row.pageDisplayName
        file = $relative
        sha256 = Get-Sha256 $resolved
    }
}

$process = Get-Process -Id $pidValue
$desktopVersion = $null
if ($process.Path -and (Test-Path $process.Path)) {
    $desktopVersion = (Get-Item $process.Path).VersionInfo.ProductVersion
}
if (-not $desktopVersion) {
    $storePackage = Get-AppxPackage -Name Microsoft.MicrosoftPowerBIDesktop -ErrorAction SilentlyContinue
    if ($storePackage) {
        $desktopVersion = [string]$storePackage.Version
    }
}
if (-not $desktopVersion) {
    throw "Could not determine the installed Power BI Desktop version."
}

$cliVersion = $installedCliVersion

$methodNames = @()
if ($manifest.methods) {
    $methodNames = @($manifest.methods | ForEach-Object { [string]$_.name } | Sort-Object)
}

$sourceCommit = (& git -C $RepoRoot rev-parse HEAD).Trim()
$fingerprint = Get-PowerBiFingerprint -Root $RepoRoot

$evidence = [ordered]@{
    schemaVersion = 1
    status = "PASS"
    capturedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    sourceCommit = $sourceCommit
    powerBiFingerprint = $fingerprint
    powerBiDesktopVersion = $desktopVersion
    desktopBridgeCliVersion = $cliVersion
    bridgeMethods = $methodNames
    pageCount = $expectedPageIds.Count
    pageOrder = $expectedPageIds
    checks = [ordered]@{
        bridgeConnected = $true
        unsavedChanges = $false
        reloadCompleted = $true
        allPagesCaptured = $true
    }
    screenshots = @($screenshotEvidence)
}

$evidencePath = Join-Path $EvidenceDir "runtime_evidence.json"
$evidence | ConvertTo-Json -Depth 50 | Set-Content $evidencePath -Encoding utf8

Write-Host "Power BI Desktop runtime evidence: PASS"
Write-Host "Evidence: $evidencePath"
Write-Host "Screenshots: $ScreenshotDir"
Write-Host "Next gate: commit the evidence files and run repository CI for fingerprint/hash validation."
