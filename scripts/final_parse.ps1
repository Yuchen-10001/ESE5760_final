Param(
    [string] $RawDir = "final_project/results/raw",
    [string] $OutCsv = "final_project/results/metrics.csv",
    [string] $IncludeRegex = "",
    [string] $ExcludeRegex = "",
    [switch] $DebugSample
)

$ErrorActionPreference = "Stop"

function Convert-ToMilliJouleFromText {
    param([string] $value, [string] $unit)
    switch ($unit) {
        "nJ" { return [double]$value * 1e-6 } # nJ -> mJ
        "pJ" { return [double]$value * 1e-9 } # pJ -> mJ
        default { return $null }
    }
}

function Convert-ToNsFromText {
    param([string] $value, [string] $unit)
    switch ($unit) {
        "ns" { return [double]$value }
        "ps" { return [double]$value / 1000.0 }
        default { return $null }
    }
}

function Convert-ToMm2FromText {
    param([string] $value, [string] $unit)
    switch ($unit) {
        "mm^2" { return [double]$value }
        "um^2" { return [double]$value / 1e6 }
        default { return $null }
    }
}

function Parse-ConfigIdFromFilename {
    param([string] $name)
    # Example: B1_SRAM_2D_N65
    # Example: TSV_SRAM3Dfine_N65_L1G0_R1.2_C050
    $rv = [ordered]@{
        run_id = $name
        case_id = $null
        process_node_nm = $null
        local_tsv_projection = $null
        global_tsv_projection = $null
        tsv_redundancy = $null
        tsv_hop_model = $null
        tsv_hop_factor = $null
    }

    if ($name -match "^(B\d+_[^_]+_[^_]+)") {
        $rv.case_id = $Matches[1]
    } elseif ($name -match "^(TSV_[^_]+)") {
        $rv.case_id = $Matches[1]
    }

    if ($name -match "_N(\d+)$") {
        $rv.process_node_nm = [int]$Matches[1]
    } elseif ($name -match "_N(\d+)_") {
        $rv.process_node_nm = [int]$Matches[1]
    }

    if ($name -match "_L(\d)G(\d)_") {
        $rv.local_tsv_projection = [int]$Matches[1]
        $rv.global_tsv_projection = [int]$Matches[2]
    }

    if ($name -match "_R([0-9.]+)_") {
        $rv.tsv_redundancy = [double]$Matches[1]
    }

    if ($name -match "_(Worst|Avg|C\d{3})$") {
        $tag = $Matches[1]
        switch ($tag) {
            "Worst" { $rv.tsv_hop_model = "WorstCase" }
            "Avg"   { $rv.tsv_hop_model = "Average" }
            default {
                $rv.tsv_hop_model = "Custom"
                if ($tag -match "^C(\d{3})$") {
                    $rv.tsv_hop_factor = [int]$Matches[1] / 1000.0
                }
            }
        }
    }

    return [pscustomobject]$rv
}

function Extract-Section {
    param(
        [string] $text,
        [string] $startMarker,
        [string] $endMarker
    )
    $start = $text.IndexOf($startMarker)
    if ($start -lt 0) { return $null }
    $end = $text.IndexOf($endMarker, $start + $startMarker.Length)
    if ($end -lt 0) { return $text.Substring($start) }
    return $text.Substring($start, $end - $start)
}

function Parse-DestinyLog {
    param([string] $path)
    $text = Get-Content $path -Raw -Encoding UTF8
    $name = [IO.Path]::GetFileNameWithoutExtension($path)
    $meta = Parse-ConfigIdFromFilename -name $name

    $summary = [ordered]@{
        cache_total_area_mm2 = $null
        cache_hit_latency_ns = $null
        cache_write_dyn_energy_nj = $null
        cache_total_leakage_mw = $null
    }

    if ($text -match "(?m)^\s*- Total Area = ([0-9.]+)mm\^2\s*$") {
        $summary.cache_total_area_mm2 = [double]$Matches[1]
    }
    if ($text -match "(?m)^\s*- Cache Hit Latency\s+= ([0-9.]+)ns\s*$") {
        $summary.cache_hit_latency_ns = [double]$Matches[1]
    }
    if ($text -match "(?m)^\s*- Cache Write Dynamic Energy = ([0-9.]+)nJ\b") {
        $summary.cache_write_dyn_energy_nj = [double]$Matches[1]
    }
    if ($text -match "(?m)^\s*- Cache Total Leakage Power\s+= ([0-9.]+)mW\s*$") {
        $summary.cache_total_leakage_mw = [double]$Matches[1]
    }

    $dataSection = Extract-Section -text $text -startMarker "CACHE DATA ARRAY DETAILS" -endMarker "CACHE TAG ARRAY DETAILS"
    $data = [ordered]@{
        data_read_latency_ns = $null
        data_write_dyn_energy_nj = $null
        data_area_mm2 = $null
        data_tsv_area_mm2 = $null
        data_tsv_read_latency_ns = $null
        data_tsv_dyn_energy_nj = $null
        data_leakage_mw = $null
    }

    if ($null -ne $dataSection) {
        if ($dataSection -match "(?m)^\s*-\s+Read Latency = ([0-9.]+)(ps|ns)\s*$") {
            $data.data_read_latency_ns = Convert-ToNsFromText $Matches[1] $Matches[2]
        }
        if ($dataSection -match "(?m)^\s*- Write Dynamic Energy = ([0-9.]+)(pJ|nJ)\s*$") {
            $v = $Matches[1]; $u = $Matches[2]
            # store in nJ for convenience
            if ($u -eq "nJ") { $data.data_write_dyn_energy_nj = [double]$v }
            if ($u -eq "pJ") { $data.data_write_dyn_energy_nj = [double]$v / 1000.0 }
        }
        if ($dataSection -match "(?m)^\s*- Total Area = .*?= ([0-9.]+)mm\^2\s*$") {
            $data.data_area_mm2 = [double]$Matches[1]
        }
        if ($dataSection -match "(?m)^\s*\|--- TSV Area\s+= ([0-9.]+)\s*(mm\^2|um\^2)\s*$") {
            $data.data_tsv_area_mm2 = Convert-ToMm2FromText $Matches[1] $Matches[2]
        }
        if ($dataSection -match "(?m)^\s*\|--- TSV Latency\s+= ([0-9.]+)ps\s*$") {
            $data.data_tsv_read_latency_ns = Convert-ToNsFromText $Matches[1] "ps"
        }
        if ($dataSection -match "(?m)^\s*\|--- TSV Dynamic Energy\s+= ([0-9.]+)pJ\s*$") {
            $data.data_tsv_dyn_energy_nj = [double]$Matches[1] / 1000.0
        }
        if ($dataSection -match "(?m)^\s*- Leakage Power = ([0-9.]+)mW\s*$") {
            $data.data_leakage_mw = [double]$Matches[1]
        }
    }

    $merged = [ordered]@{}
    foreach ($p in $meta.PSObject.Properties) {
        $merged[$p.Name] = $p.Value
    }
    foreach ($k in $summary.Keys) {
        $merged[$k] = $summary[$k]
    }
    foreach ($k in $data.Keys) {
        $merged[$k] = $data[$k]
    }
    return [pscustomobject]$merged
}

if (!(Test-Path $RawDir)) {
    throw "Missing raw directory: $RawDir"
}

$rawFiles = Get-ChildItem -Path $RawDir -Filter *.txt -File | Sort-Object Name
if ($rawFiles.Count -eq 0) {
    throw "No raw logs found in $RawDir. Run scripts/final_run.ps1 first."
}

if ($IncludeRegex) {
    $rawFiles = $rawFiles | Where-Object { $_.Name -match $IncludeRegex }
}
if ($ExcludeRegex) {
    $rawFiles = $rawFiles | Where-Object { $_.Name -notmatch $ExcludeRegex }
}
if ($rawFiles.Count -eq 0) {
    throw "No raw logs matched Include/Exclude filters."
}

$rows = foreach ($f in $rawFiles) { Parse-DestinyLog -path $f.FullName }

if ($DebugSample) {
    $rows | Select-Object -First 1 | Format-List * | Out-String | Write-Host
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutCsv) | Out-Null
$rows | Export-Csv -Path $OutCsv -NoTypeInformation -Encoding UTF8

Write-Host ("Wrote {0} rows to {1}" -f $rows.Count, $OutCsv)
