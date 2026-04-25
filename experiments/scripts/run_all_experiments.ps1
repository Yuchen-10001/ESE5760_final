# run_all_experiments.ps1
#
# Runs destiny.exe on every config in experiments/configs/
# Must be executed from the project root (final/) so that
# cell file paths like "config/sample_SRAM.cell" resolve correctly.
#
# Usage (from final/):
#   powershell -ExecutionPolicy Bypass -File experiments\scripts\run_all_experiments.ps1
#
# Outputs are saved to experiments/results/<cfg_basename>_output.txt

param(
    [string]$ConfigDir  = "experiments\configs",
    [string]$ResultsDir = "experiments\results",
    [string]$DestinyExe = ".\destiny.exe"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Verify we are in the right directory
if (-not (Test-Path $DestinyExe)) {
    Write-Error "destiny.exe not found at '$DestinyExe'. Run this script from the final/ project root."
    exit 1
}

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$configs = Get-ChildItem "$ConfigDir\*.cfg" | Sort-Object Name
$total   = $configs.Count
$passed  = 0
$failed  = 0
$index   = 0

Write-Host ""
Write-Host "=== ESE5760 Final Project — DESTINY batch run ==="
Write-Host "  Configs : $ConfigDir  ($total files)"
Write-Host "  Results : $ResultsDir"
Write-Host "  Engine  : $DestinyExe"
Write-Host ""

foreach ($cfg in $configs) {
    $index++
    $name       = $cfg.BaseName
    $outputFile = "$ResultsDir\${name}_output.txt"

    Write-Host "[$index/$total] $name ... " -NoNewline

    $proc = Start-Process -FilePath $DestinyExe `
                          -ArgumentList $cfg.FullName `
                          -RedirectStandardOutput $outputFile `
                          -RedirectStandardError  "$ResultsDir\${name}_stderr.txt" `
                          -NoNewWindow -Wait -PassThru

    if ($proc.ExitCode -eq 0) {
        Write-Host "OK" -ForegroundColor Green
        $passed++
        # Remove empty stderr file to keep results dir clean
        if ((Get-Item "$ResultsDir\${name}_stderr.txt").Length -eq 0) {
            Remove-Item "$ResultsDir\${name}_stderr.txt"
        }
    } else {
        Write-Host "FAILED (exit $($proc.ExitCode))" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "=== Done: $passed passed, $failed failed ==="
Write-Host ""
if ($failed -gt 0) {
    Write-Host "Check *_stderr.txt files in $ResultsDir for error details." -ForegroundColor Yellow
}
