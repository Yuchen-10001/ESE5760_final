Param(
    [string] $MetricsCsv = "final_project/results/metrics.csv",
    [string] $OutDir = "final_project/figures"
)

$ErrorActionPreference = "Stop"

function New-SvgLineChart {
    param(
        [Parameter(Mandatory = $true)] [string] $Title,
        [Parameter(Mandatory = $true)] [string] $XLabel,
        [Parameter(Mandatory = $true)] [string] $YLabel,
        [Parameter(Mandatory = $true)] [int[]] $XValues,
        [Parameter(Mandatory = $true)] $Series, # array of @{ name=...; points=@(@{x=..;y=..},...) }
        [int] $Width = 960,
        [int] $Height = 520
    )

    $marginL = 80
    $marginR = 30
    $marginT = 55
    $marginB = 70
    $plotW = $Width - $marginL - $marginR
    $plotH = $Height - $marginT - $marginB

    $allY = @()
    foreach ($s in $Series) {
        foreach ($p in $s.points) {
            if ($null -ne $p.y -and $p.y -ne "") { $allY += [double]$p.y }
        }
    }
    if ($allY.Count -eq 0) { throw "No Y values found for $Title" }
    $yMin = ($allY | Measure-Object -Minimum).Minimum
    $yMax = ($allY | Measure-Object -Maximum).Maximum
    if ($yMax -eq $yMin) { $yMax = $yMin + 1 }
    $pad = 0.08 * ($yMax - $yMin)
    $yMin = $yMin - $pad
    $yMax = $yMax + $pad

    $xMin = ($XValues | Measure-Object -Minimum).Minimum
    $xMax = ($XValues | Measure-Object -Maximum).Maximum
    $xSpan = [double]($xMax - $xMin)
    if ($xSpan -eq 0) { $xSpan = 1 }

    function Xpx([double] $x) {
        $nx = ($x - $xMin) / $xSpan
        return [math]::Round($marginL + $nx * $plotW, 2)
    }
    function Ypx([double] $y) {
        $ny = ($y - $yMin) / ($yMax - $yMin)
        return [math]::Round($marginT + (1 - $ny) * $plotH, 2)
    }

    $colors = @("#2563eb", "#16a34a", "#dc2626", "#7c3aed", "#0f766e", "#c2410c")

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("<?xml version=""1.0"" encoding=""UTF-8""?>")
    [void]$sb.AppendLine("<svg xmlns=""http://www.w3.org/2000/svg"" width=""$Width"" height=""$Height"" viewBox=""0 0 $Width $Height"">")
    [void]$sb.AppendLine("<rect x=""0"" y=""0"" width=""$Width"" height=""$Height"" fill=""white""/>")
    [void]$sb.AppendLine("<style>
        .title{font:600 18px sans-serif;fill:#0f172a}
        .axis{stroke:#334155;stroke-width:1}
        .grid{stroke:#e2e8f0;stroke-width:1}
        .tick{font:12px sans-serif;fill:#334155}
        .label{font:13px sans-serif;fill:#0f172a}
        .legend{font:12px sans-serif;fill:#0f172a}
    </style>")

    # Title
    [void]$sb.AppendLine("<text class=""title"" x=""$marginL"" y=""30"">$Title</text>")

    # Axes
    $x0 = $marginL
    $y0 = $marginT + $plotH
    $x1 = $marginL + $plotW
    $y1 = $marginT
    [void]$sb.AppendLine("<line class=""axis"" x1=""$x0"" y1=""$y0"" x2=""$x1"" y2=""$y0""/>")
    [void]$sb.AppendLine("<line class=""axis"" x1=""$x0"" y1=""$y0"" x2=""$x0"" y2=""$y1""/>")

    # X ticks (process node)
    foreach ($x in $XValues) {
        $xp = Xpx $x
        [void]$sb.AppendLine("<line class=""grid"" x1=""$xp"" y1=""$y0"" x2=""$xp"" y2=""$y1""/>")
        [void]$sb.AppendLine("<text class=""tick"" x=""$xp"" y=""$($y0+20)"" text-anchor=""middle"">$x</text>")
    }

    # Y ticks
    $yTicks = 5
    for ($i=0; $i -le $yTicks; $i++) {
        $t = $yMin + ($i / $yTicks) * ($yMax - $yMin)
        $yp = Ypx $t
        [void]$sb.AppendLine("<line class=""grid"" x1=""$x0"" y1=""$yp"" x2=""$x1"" y2=""$yp""/>")
        [void]$sb.AppendLine(("<text class=""tick"" x=""{0}"" y=""{1}"" text-anchor=""end"">{2}</text>" -f ($x0-10), ($yp+4), ([math]::Round($t, 3))))
    }

    # Labels
    [void]$sb.AppendLine("<text class=""label"" x=""$($marginL + $plotW/2)"" y=""$($Height-20)"" text-anchor=""middle"">$XLabel</text>")
    [void]$sb.AppendLine("<text class=""label"" x=""20"" y=""$($marginT + $plotH/2)"" text-anchor=""middle"" transform=""rotate(-90 20 $($marginT + $plotH/2))"">$YLabel</text>")

    # Series lines + points
    for ($si=0; $si -lt $Series.Count; $si++) {
        $s = $Series[$si]
        $color = $colors[$si % $colors.Count]
        $pts = @()
        foreach ($p in ($s.points | Sort-Object { [int]$_.x })) {
            if ($null -eq $p.y -or $p.y -eq "") { continue }
            $pts += ("{0},{1}" -f (Xpx $p.x), (Ypx $p.y))
        }
        if ($pts.Count -ge 2) {
            [void]$sb.AppendLine("<polyline fill=""none"" stroke=""$color"" stroke-width=""2.5"" points=""$($pts -join ' ')""/>")
        }
        foreach ($p in ($s.points | Sort-Object { [int]$_.x })) {
            if ($null -eq $p.y -or $p.y -eq "") { continue }
            $cx = Xpx $p.x
            $cy = Ypx $p.y
            [void]$sb.AppendLine("<circle cx=""$cx"" cy=""$cy"" r=""3.5"" fill=""$color""/>")
        }
    }

    # Legend
    $lx = $marginL + $plotW - 10
    $ly = 18
    for ($si=0; $si -lt $Series.Count; $si++) {
        $s = $Series[$si]
        $color = $colors[$si % $colors.Count]
        $y = $marginT + $si * 18
        [void]$sb.AppendLine("<rect x=""$($lx-140)"" y=""$($y-10)"" width=""12"" height=""12"" fill=""$color""/>")
        [void]$sb.AppendLine("<text class=""legend"" x=""$($lx-122)"" y=""$($y)"" text-anchor=""start"">$($s.name)</text>")
    }

    [void]$sb.AppendLine("</svg>")
    return $sb.ToString()
}

function New-SvgBarChart {
    param(
        [Parameter(Mandatory = $true)] [string] $Title,
        [Parameter(Mandatory = $true)] [string] $XLabel,
        [Parameter(Mandatory = $true)] [string] $YLabel,
        [Parameter(Mandatory = $true)] $Bars, # array of @{ label=...; value=...; color=... }
        [int] $Width = 960,
        [int] $Height = 520
    )

    $marginL = 90
    $marginR = 30
    $marginT = 55
    $marginB = 110
    $plotW = $Width - $marginL - $marginR
    $plotH = $Height - $marginT - $marginB

    $vals = $Bars | ForEach-Object { [double]$_.value }
    $yMin = 0
    $yMax = ($vals | Measure-Object -Maximum).Maximum
    if ($yMax -le 0) { $yMax = 1 }
    $yMax = $yMax * 1.12

    function Ypx([double] $y) {
        $ny = ($y - $yMin) / ($yMax - $yMin)
        return [math]::Round($marginT + (1 - $ny) * $plotH, 2)
    }

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("<?xml version=""1.0"" encoding=""UTF-8""?>")
    [void]$sb.AppendLine("<svg xmlns=""http://www.w3.org/2000/svg"" width=""$Width"" height=""$Height"" viewBox=""0 0 $Width $Height"">")
    [void]$sb.AppendLine("<rect x=""0"" y=""0"" width=""$Width"" height=""$Height"" fill=""white""/>")
    [void]$sb.AppendLine("<style>
        .title{font:600 18px sans-serif;fill:#0f172a}
        .axis{stroke:#334155;stroke-width:1}
        .grid{stroke:#e2e8f0;stroke-width:1}
        .tick{font:12px sans-serif;fill:#334155}
        .label{font:13px sans-serif;fill:#0f172a}
    </style>")
    [void]$sb.AppendLine("<text class=""title"" x=""$marginL"" y=""30"">$Title</text>")

    $x0 = $marginL
    $y0 = $marginT + $plotH
    $x1 = $marginL + $plotW
    $y1 = $marginT
    [void]$sb.AppendLine("<line class=""axis"" x1=""$x0"" y1=""$y0"" x2=""$x1"" y2=""$y0""/>")
    [void]$sb.AppendLine("<line class=""axis"" x1=""$x0"" y1=""$y0"" x2=""$x0"" y2=""$y1""/>")

    # Y ticks
    $yTicks = 5
    for ($i=0; $i -le $yTicks; $i++) {
        $t = $yMin + ($i / $yTicks) * ($yMax - $yMin)
        $yp = Ypx $t
        [void]$sb.AppendLine("<line class=""grid"" x1=""$x0"" y1=""$yp"" x2=""$x1"" y2=""$yp""/>")
        [void]$sb.AppendLine(("<text class=""tick"" x=""{0}"" y=""{1}"" text-anchor=""end"">{2}</text>" -f ($x0-10), ($yp+4), ([math]::Round($t, 3))))
    }

    # Bars
    $n = $Bars.Count
    $gap = 12
    $barW = [math]::Max(12, [math]::Floor(($plotW - ($n+1)*$gap) / $n))
    for ($i=0; $i -lt $n; $i++) {
        $b = $Bars[$i]
        $x = $x0 + $gap + $i * ($barW + $gap)
        $y = Ypx ([double]$b.value)
        $h = $y0 - $y
        $c = $b.color
        [void]$sb.AppendLine("<rect x=""$x"" y=""$y"" width=""$barW"" height=""$h"" fill=""$c""/>")
        [void]$sb.AppendLine("<text class=""tick"" x=""$($x + $barW/2)"" y=""$($y0+18)"" text-anchor=""middle"">$($b.label)</text>")
    }

    [void]$sb.AppendLine("<text class=""label"" x=""$($marginL + $plotW/2)"" y=""$($Height-20)"" text-anchor=""middle"">$XLabel</text>")
    [void]$sb.AppendLine("<text class=""label"" x=""20"" y=""$($marginT + $plotH/2)"" text-anchor=""middle"" transform=""rotate(-90 20 $($marginT + $plotH/2))"">$YLabel</text>")
    [void]$sb.AppendLine("</svg>")
    return $sb.ToString()
}

if (!(Test-Path $MetricsCsv)) {
    throw "Missing metrics CSV: $MetricsCsv. Run scripts/final_parse.ps1 first."
}

$rows = Import-Csv $MetricsCsv
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# ----------------------------
# Baseline scaling: 4 cases
# ----------------------------
$baseline = $rows | Where-Object { $_.case_id -match '^B[1-4]_' }
$nodes = @($baseline | Select-Object -ExpandProperty process_node_nm | ForEach-Object { [int]$_ } | Sort-Object -Unique)

$cases = @(
    @{ id="B1_SRAM_2D";  name="SRAM 2D";  },
    @{ id="B2_SRAM_3D";  name="SRAM 3D (4-layer, coarse)"; },
    @{ id="B3_eDRAM_2D"; name="eDRAM 2D"; },
    @{ id="B4_eDRAM_3D"; name="eDRAM 3D (4-layer, coarse)"; }
)

function Build-Series($field) {
    $series = @()
    foreach ($c in $cases) {
        $pts = @()
        foreach ($n in $nodes) {
            $row = $baseline | Where-Object { $_.case_id -eq $c.id -and [int]$_.process_node_nm -eq $n } | Select-Object -First 1
            $y = if ($null -ne $row) { $row.$field } else { $null }
            $pts += @{ x = $n; y = $y }
        }
        $series += @{ name = $c.name; points = $pts }
    }
    return ,$series
}

$areaSvg = New-SvgLineChart -Title "Baseline Scaling: Total Area" -XLabel "Process Node (nm)" -YLabel "Total Cache Area (mm^2)" -XValues $nodes -Series (Build-Series "cache_total_area_mm2")
Set-Content -Path (Join-Path $OutDir "baseline_total_area.svg") -Value $areaSvg -Encoding UTF8

$latSvg = New-SvgLineChart -Title "Baseline Scaling: Hit Latency" -XLabel "Process Node (nm)" -YLabel "Cache Hit Latency (ns)" -XValues $nodes -Series (Build-Series "cache_hit_latency_ns")
Set-Content -Path (Join-Path $OutDir "baseline_hit_latency.svg") -Value $latSvg -Encoding UTF8

$weSvg = New-SvgLineChart -Title "Baseline Scaling: Write Dynamic Energy" -XLabel "Process Node (nm)" -YLabel "Cache Write Dynamic Energy (nJ/access)" -XValues $nodes -Series (Build-Series "cache_write_dyn_energy_nj")
Set-Content -Path (Join-Path $OutDir "baseline_write_energy.svg") -Value $weSvg -Encoding UTF8

# ----------------------------
# TSV sweep: summarize TSV dynamic energy (data array) for R=1.0, different hop models
# ----------------------------
$tsv = $rows | Where-Object { $_.case_id -like "TSV_*" }
$tsvR1 = $tsv | Where-Object { $_.tsv_redundancy -eq "1" -and $_.local_tsv_projection -eq "0" -and $_.global_tsv_projection -eq "0" }

if ($tsvR1.Count -gt 0) {
    $order = @(
        @{ label="Worst"; model="WorstCase"; factor="" ; color="#2563eb" },
        @{ label="Avg";   model="Average";   factor="" ; color="#16a34a" },
        @{ label="C0.25"; model="Custom";    factor="0.25"; color="#dc2626" },
        @{ label="C0.50"; model="Custom";    factor="0.5";  color="#7c3aed" },
        @{ label="C0.75"; model="Custom";    factor="0.75"; color="#0f766e" }
    )
    $bars = @()
    foreach ($o in $order) {
        $row = $tsvR1 | Where-Object {
            $_.tsv_hop_model -eq $o.model -and (($o.factor -eq "" -and ($_.tsv_hop_factor -eq "" -or $null -eq $_.tsv_hop_factor)) -or ($_.tsv_hop_factor -eq $o.factor))
        } | Select-Object -First 1
        if ($null -ne $row) {
            $bars += @{
                label = $o.label
                value = [double]$row.data_tsv_dyn_energy_nj
                color = $o.color
            }
        }
    }

    if ($bars.Count -gt 0) {
        $barSvg = New-SvgBarChart -Title "TSV Sensitivity (SRAM 3D fine, 65nm, R=1.0): TSV Dynamic Energy" -XLabel "Hop Model" -YLabel "Data TSV Dynamic Energy (nJ/access)" -Bars $bars
        Set-Content -Path (Join-Path $OutDir "tsv_hopmodel_energy.svg") -Value $barSvg -Encoding UTF8
    }
}

Write-Host ("Wrote SVG figures to {0}" -f $OutDir)

