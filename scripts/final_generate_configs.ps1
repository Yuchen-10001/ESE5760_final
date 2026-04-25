Param(
    [int[]] $ProcessNodes = @(65, 45, 32, 22),
    [string] $TemplatesDir = "config/final/templates",
    [string] $OutDir = "config/final/generated"
)

$ErrorActionPreference = "Stop"

function Set-CfgScalar {
    param(
        [Parameter(Mandatory = $true)] [string] $CfgText,
        [Parameter(Mandatory = $true)] [string] $Key,
        [Parameter(Mandatory = $true)] [string] $Value
    )
    $escapedKey = [regex]::Escape($Key)
    $pattern = "(?m)^(\\s*-$escapedKey\\s*:\\s*).*$"
    if ($CfgText -match $pattern) {
        return [regex]::Replace($CfgText, $pattern, "`$1$Value")
    }
    return ($CfgText.TrimEnd() + "`r`n-$($Key): $Value`r`n")
}

function Write-GeneratedCfg {
    param(
        [Parameter(Mandatory = $true)] [string] $TemplatePath,
        [Parameter(Mandatory = $true)] [string] $OutPath,
        [Parameter(Mandatory = $true)] [hashtable] $Overrides
    )

    $text = Get-Content $TemplatePath -Raw -Encoding UTF8
    foreach ($k in $Overrides.Keys) {
        $text = Set-CfgScalar -CfgText $text -Key $k -Value $Overrides[$k]
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutPath) | Out-Null
    Set-Content -Path $OutPath -Value $text -Encoding UTF8
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# ----------------------------
# Baseline scaling configs
# ----------------------------
$baselineTemplates = @(
    @{ id = "B1_SRAM_2D";            path = Join-Path $TemplatesDir "B1_SRAM_2D_base.cfg" },
    @{ id = "B2_SRAM_3D_coarse";     path = Join-Path $TemplatesDir "B2_SRAM_3D_coarse_base.cfg" },
    @{ id = "B3_eDRAM_2D";           path = Join-Path $TemplatesDir "B3_eDRAM_2D_base.cfg" },
    @{ id = "B4_eDRAM_3D_coarse";    path = Join-Path $TemplatesDir "B4_eDRAM_3D_coarse_base.cfg" }
)

foreach ($tmpl in $baselineTemplates) {
    foreach ($node in $ProcessNodes) {
        $out = Join-Path $OutDir ("{0}_N{1}.cfg" -f $tmpl.id, $node)
        Write-GeneratedCfg -TemplatePath $tmpl.path -OutPath $out -Overrides @{
            "ProcessNode" = "$node"
        }
    }
}

# ----------------------------
# TSV sensitivity sweep configs
# ----------------------------
$tsvBase = Join-Path $TemplatesDir "TSV_SRAM_3D_fine_sweep_base.cfg"

$tsvNodes = @(
    65
)

$projections = @(
    @{ local = 0; global = 0; label = "Agg_Agg" },
    @{ local = 1; global = 0; label = "Con_Agg" },
    @{ local = 0; global = 1; label = "Agg_Con" },
    @{ local = 1; global = 1; label = "Con_Con" }
)

$redundancies = @(1.0, 1.2, 1.5)

$hopModels = @(
    @{ model = "WorstCase"; factor = $null; label = "Worst" },
    @{ model = "Average";   factor = $null; label = "Avg" },
    @{ model = "Custom";    factor = 0.25;  label = "C025" },
    @{ model = "Custom";    factor = 0.50;  label = "C050" },
    @{ model = "Custom";    factor = 0.75;  label = "C075" }
)

foreach ($node in $tsvNodes) {
    foreach ($p in $projections) {
        foreach ($r in $redundancies) {
            foreach ($h in $hopModels) {
                $id = "TSV_SRAM3Dfine_N{0}_L{1}G{2}_R{3}_{4}" -f $node, $p.local, $p.global, $r, $h.label
                $out = Join-Path $OutDir ("{0}.cfg" -f $id)
                $ov = @{
                    "ProcessNode" = "$node"
                    "LocalTSVProjection" = "$($p.local)"
                    "GlobalTSVProjection" = "$($p.global)"
                    "TSVRedundancy" = "$r"
                    "TSVHopModel" = "$($h.model)"
                }
                if ($null -ne $h.factor) {
                    $ov["TSVHopFactor"] = "$($h.factor)"
                }
                Write-GeneratedCfg -TemplatePath $tsvBase -OutPath $out -Overrides $ov
            }
        }
    }
}

Write-Host ("Generated configs in {0}" -f $OutDir)
