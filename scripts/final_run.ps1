Param(
    [string] $GeneratedDir = "config/final/generated",
    [string] $ResultsDir = "final_project/results/raw",
    [string] $ExePath = "destiny_tsv_stage2.exe",
    [string] $IncludeRegex = "",
    [string] $ExcludeRegex = "",
    [int] $MaxRuns = 0
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $GeneratedDir)) {
    throw "Missing generated configs folder: $GeneratedDir. Run scripts/final_generate_configs.ps1 first."
}

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$repoRoot = (Resolve-Path ".").Path
$configDir = Join-Path $repoRoot "config"
$exe = Join-Path $repoRoot $ExePath

if (!(Test-Path $exe)) {
    throw "Missing executable: $exe"
}

$cfgFiles = Get-ChildItem -Path $GeneratedDir -Filter *.cfg -File | Sort-Object Name
if ($cfgFiles.Count -eq 0) {
    throw "No .cfg files found in $GeneratedDir"
}

if ($IncludeRegex) {
    $cfgFiles = $cfgFiles | Where-Object { $_.Name -match $IncludeRegex }
}
if ($ExcludeRegex) {
    $cfgFiles = $cfgFiles | Where-Object { $_.Name -notmatch $ExcludeRegex }
}
if ($MaxRuns -gt 0) {
    $cfgFiles = $cfgFiles | Select-Object -First $MaxRuns
}

if ($cfgFiles.Count -eq 0) {
    throw "No .cfg files matched Include/Exclude filters."
}

Push-Location $configDir
try {
    foreach ($cfg in $cfgFiles) {
        $cfgRelFromConfig = (Resolve-Path $cfg.FullName).Path.Substring($configDir.Length + 1)
        $safeName = [IO.Path]::GetFileNameWithoutExtension($cfg.Name)
        $outPath = Join-Path (Resolve-Path (Join-Path $repoRoot $ResultsDir)).Path ("{0}.txt" -f $safeName)

        Write-Host ("Running {0}" -f $cfgRelFromConfig)
        & $exe $cfgRelFromConfig 2>&1 | Out-File -FilePath $outPath -Encoding UTF8
    }
}
finally {
    Pop-Location
}

Write-Host ("Raw logs written to {0}" -f $ResultsDir)
