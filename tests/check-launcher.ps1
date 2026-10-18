# Run with: pwsh -NoProfile -File tests/check-launcher.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$launcher = Join-Path $root 'start-notebooks.ps1'
$originalLocation = Get-Location

function Assert-True($Condition, $Message) {
    if (-not $Condition) { throw $Message }
}

try {
    # Script paths must work even when the caller is outside the repository.
    Set-Location ([System.IO.Path]::GetTempPath())
    $default = & $launcher -DryRun
    Assert-True ($default.Language -eq 'en' -and $default.Module -eq 'vision') 'Default must be English vision.'
    foreach ($module in @('vision', 'pytorch', 'paddle', 'detection')) {
        $route = & $launcher -Module $module -DryRun
        Assert-True ($route.Language -eq 'en' -and $route.Module -eq $module) "Incorrect English route: $module"
        Assert-True (Test-Path -LiteralPath (Join-Path $route.ModuleRoot 'uv.lock')) "Missing English lockfile: $module"
        Assert-True (Test-Path -LiteralPath $route.NotebookRoot) "Missing English notebooks: $module"
    }
    foreach ($module in @('vision', 'pytorch', 'paddle')) {
        $route = & $launcher -Language zh-CN -Module $module -DryRun
        Assert-True ($route.Language -eq 'zh-CN' -and $route.Module -eq $module) "Incorrect Chinese route: $module"
        Assert-True (Test-Path -LiteralPath $route.WorkingDirectory) "Missing Chinese notebooks: $module"
        Assert-True (Test-Path -LiteralPath (Join-Path $route.ModuleRoot 'requirements.txt')) "Missing Chinese requirements: $module"
        Assert-True ($route.WorkingDirectory -notlike '*english*') 'Chinese route selected English course.'
    }
    $detection = & $launcher -Language zh-CN -Module detection -DryRun
    Assert-True ($detection.Language -eq 'zh-CN') 'Chinese detection language was lost.'
    Assert-True ($detection.ModuleRoot -eq (& $launcher -Module detection -DryRun).ModuleRoot) 'Detection must share its locked environment.'
    Assert-True ($detection.NotebookRoot -eq (Join-Path $root '02-object-detection/notebooks')) 'Chinese detection must open the Chinese notebook directory.'
    $legacy = & (Join-Path $root 'english/start-notebooks.ps1') -DryRun
    Assert-True ($legacy.Module -eq 'vision') 'Existing English launcher must default to vision.'
    Write-Output 'PASS: default, all language/module routes, shared detection environment, and invocation outside the repository.'
} finally {
    Set-Location $originalLocation
}
