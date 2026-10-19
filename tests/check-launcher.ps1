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

    # One uv project for the whole course: the repository root.
    foreach ($file in @('pyproject.toml', 'uv.lock', '.python-version')) {
        Assert-True (Test-Path -LiteralPath (Join-Path $root $file) -PathType Leaf) "Missing root uv file: $file"
    }

    $default = & $launcher -DryRun
    Assert-True ($default.Language -eq 'zh-CN' -and $default.Module -eq 'vision') 'The root launcher must default to the Chinese masters (vision).'
    foreach ($module in @('vision', 'pytorch', 'paddle', 'detection')) {
        $route = & $launcher -Language en -Module $module -DryRun
        Assert-True ($route.Language -eq 'en' -and $route.Module -eq $module) "Incorrect English route: $module"
        Assert-True ($route.ProjectRoot -eq $root) "English route lost the root uv project: $module"
        Assert-True (Test-Path -LiteralPath $route.NotebookRoot) "Missing English notebooks: $module"
        Assert-True (Test-Path -LiteralPath (Join-Path $route.ModuleRoot 'README.md')) "Missing English module README: $module"
    }
    foreach ($module in @('vision', 'pytorch', 'paddle', 'detection')) {
        $route = & $launcher -Language zh-CN -Module $module -DryRun
        Assert-True ($route.Language -eq 'zh-CN' -and $route.Module -eq $module) "Incorrect Chinese route: $module"
        Assert-True ($route.ProjectRoot -eq $root) "Chinese route lost the root uv project: $module"
        Assert-True (Test-Path -LiteralPath $route.WorkingDirectory) "Missing Chinese notebooks: $module"
        Assert-True ($route.WorkingDirectory -notlike '*english*') 'Chinese route selected English course.'
    }
    # 00-machine-learning has no launcher route yet, but it runs in the same root environment.
    Assert-True (Test-Path -LiteralPath (Join-Path $root '00-machine-learning/notebooks')) 'Missing machine-learning notebooks.'

    $detection = & $launcher -Language zh-CN -Module detection -DryRun
    Assert-True ($detection.Language -eq 'zh-CN') 'Chinese detection language was lost.'
    Assert-True ($detection.ProjectRoot -eq (& $launcher -Language en -Module detection -DryRun).ProjectRoot) 'Both language editions must share the root uv project.'
    Assert-True ($detection.NotebookRoot -eq (Join-Path $root '02-object-detection/notebooks')) 'Chinese detection must open the Chinese notebook directory.'

    # Module folders must not carry their own uv project any more.
    foreach ($moduleRoot in @('01-image-classification', '03-sentiment-analysis/pytorch', '03-sentiment-analysis/paddle',
                              'english/01-image-classification', 'english/02-object-detection',
                              'english/03-sentiment-analysis/pytorch', 'english/03-sentiment-analysis/paddle')) {
        foreach ($file in @('pyproject.toml', 'uv.lock', '.python-version', 'requirements.txt')) {
            Assert-True (-not (Test-Path -LiteralPath (Join-Path (Join-Path $root $moduleRoot) $file))) "Module-level uv file survived: $moduleRoot/$file"
        }
    }

    $legacy = & (Join-Path $root 'english/start-notebooks.ps1') -DryRun
    Assert-True ($legacy.Module -eq 'vision') 'Existing English launcher must default to vision.'
    Assert-True ($legacy.Language -eq 'en') 'The English shim must keep the English language route.'
    $legacyChinese = & (Join-Path $root 'english/start-notebooks.ps1') -Language zh-CN -Module detection -DryRun
    Assert-True ($legacyChinese.NotebookRoot -eq (Join-Path $root '02-object-detection/notebooks')) 'The English shim must forward -Language zh-CN.'
    Write-Output 'PASS: root uv project, zh-CN launcher default, all language/module routes, shared environment, and invocation outside the repository.'
} finally {
    Set-Location $originalLocation
}
