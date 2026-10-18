param(
    [ValidateSet('en', 'zh-CN')]
    [string]$Language = 'en',
    [ValidateSet('vision', 'pytorch', 'paddle', 'detection')]
    [string]$Module = 'vision',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

if ($Language -eq 'en') {
    & (Join-Path $PSScriptRoot 'english/start-notebooks.ps1') -Module $Module -DryRun:$DryRun
    return
}

if ($Module -eq 'detection') {
    & (Join-Path $PSScriptRoot 'english/start-notebooks.ps1') -Module detection -Language zh-CN -DryRun:$DryRun
    return
}
$modulePaths = @{
    vision = '01-image-classification'
    pytorch = '03-sentiment-analysis/pytorch'
    paddle = '03-sentiment-analysis/paddle'
}
$moduleRoot = Join-Path $PSScriptRoot $modulePaths[$Module]
$pythonPath = Join-Path $moduleRoot '.venv/Scripts/python.exe'
$notebookRoot = Join-Path $moduleRoot 'notebooks'
if ($DryRun) {
    [pscustomobject]@{
        Language = $Language
        Module = $Module
        ModuleRoot = $moduleRoot
        WorkingDirectory = $notebookRoot
        Python = $pythonPath
    }
    return
}
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Create $moduleRoot/.venv and install its requirements first. See docs/environment-setup.zh-CN.md."
}
Push-Location $notebookRoot
try {
    & $pythonPath -m jupyterlab --notebook-dir .
    if ($LASTEXITCODE -ne 0) { throw 'JupyterLab failed. Read the preceding error message.' }
} finally {
    Pop-Location
}
