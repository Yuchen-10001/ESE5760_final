# parse_results.ps1
#
# Reads every DESTINY output file in experiments/results/ and extracts
# key metrics into experiments/data/results.csv
#
# Metrics extracted (from CACHE DESIGN -- SUMMARY):
#   total_area_mm2      Total Area (mm^2)
#   read_latency_ns     Cache Hit Latency (ns)
#   write_latency_ns    Cache Write Latency (ns)
#   write_energy_nJ     Cache Write Dynamic Energy (nJ/access)
#   leakage_power_mW    Cache Total Leakage Power (mW)
#
# Usage (from final/ or experiments/scripts/):
#   powershell -ExecutionPolicy Bypass -File experiments\scripts\parse_results.ps1

$ResultsDir = "experiments\results"
$DataDir    = "experiments\data"
$OutputCsv  = "$DataDir\results.csv"

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

function Extract-Value {
    param([string]$Text, [string]$Pattern)
    $m = [regex]::Match($Text, $Pattern)
    if ($m.Success) { return [double]$m.Groups[1].Value }
    return $null
}

function Parse-Filename {
    param([string]$Stem)
    # Remove trailing _output
    $Stem = $Stem -replace '_output$', ''

    if ($Stem -match '^TSV_') {
        $info = @{ experiment=2; technology='3D_SRAM'; node_nm=32 }
        $suffix = $Stem -replace '^TSV_3D_SRAM_32nm_', ''

        if ($suffix -match '^LocalTSV(\d+)$') {
            $info.tsv_param  = 'LocalTSVProjection'
            $info.tsv_value  = [int]$Matches[1]
        } elseif ($suffix -match '^GlobalTSV(\d+)$') {
            $info.tsv_param  = 'GlobalTSVProjection'
            $info.tsv_value  = [int]$Matches[1]
        } elseif ($suffix -match '^Redundancy(\d+)p(\d+)$') {
            $info.tsv_param  = 'TSVRedundancy'
            $info.tsv_value  = [double]("$($Matches[1]).$($Matches[2])")
        } else {
            $info.tsv_param  = 'unknown'
            $info.tsv_value  = $suffix
        }
        return $info
    } else {
        if ($Stem -match '^(2D_SRAM|3D_SRAM|2D_eDRAM|3D_eDRAM)_(\d+)nm$') {
            return @{
                experiment = 1
                technology = $Matches[1]
                node_nm    = [int]$Matches[2]
                tsv_param  = ''
                tsv_value  = ''
            }
        }
        return @{ experiment='?'; technology=$Stem; node_nm=''; tsv_param=''; tsv_value='' }
    }
}

$rows = @()
$files = Get-ChildItem "$ResultsDir\*_output.txt" | Sort-Object Name

foreach ($file in $files) {
    $text  = Get-Content $file.FullName -Raw -Encoding UTF8
    $meta  = Parse-Filename $file.BaseName

    $area    = Extract-Value $text 'Total Area\s*=\s*([\d.]+)\s*mm\^2'
    $readLat = Extract-Value $text 'Cache Hit Latency\s*=\s*([\d.]+)\s*ns'
    $writLat = Extract-Value $text 'Cache Write Latency\s*=\s*([\d.]+)\s*ns'
    $writEn  = Extract-Value $text 'Cache Write Dynamic Energy\s*=\s*([\d.]+)\s*nJ'
    $leakage = Extract-Value $text 'Cache Total Leakage Power\s*=\s*([\d.]+)\s*mW'

    $missing = @()
    if ($null -eq $area)    { $missing += 'total_area_mm2' }
    if ($null -eq $readLat) { $missing += 'read_latency_ns' }
    if ($null -eq $writLat) { $missing += 'write_latency_ns' }
    if ($null -eq $writEn)  { $missing += 'write_energy_nJ' }
    if ($null -eq $leakage) { $missing += 'leakage_power_mW' }
    $notes = if ($missing) { "missing: $($missing -join ', ')" } else { '' }

    $row = [PSCustomObject]@{
        filename         = $file.Name
        experiment       = $meta.experiment
        technology       = $meta.technology
        node_nm          = $meta.node_nm
        tsv_param        = $meta.tsv_param
        tsv_value        = $meta.tsv_value
        total_area_mm2   = $area
        read_latency_ns  = $readLat
        write_latency_ns = $writLat
        write_energy_nJ  = $writEn
        leakage_power_mW = $leakage
        notes            = $notes
    }
    $rows += $row

    $status = if ($notes) { "WARN ($notes)" } else { 'OK' }
    Write-Host "  $($file.Name.PadRight(55)) $status"
}

$rows | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "$($rows.Count) rows written to $OutputCsv"
$warnCount = ($rows | Where-Object { $_.notes -ne '' }).Count
if ($warnCount -gt 0) {
    Write-Host "WARNING: $warnCount files had missing metrics." -ForegroundColor Yellow
}
