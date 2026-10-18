param(
    [ValidateSet('paddle', 'pytorch', 'vision', 'detection')]
    [string]$Module = 'vision',
    [ValidateSet('en', 'zh-CN')]
    [string]$Language = 'en',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$modulePaths = @{
    paddle = '03-sentiment-analysis/paddle'
    pytorch = '03-sentiment-analysis/pytorch'
    vision = '01-image-classification'
    detection = '02-object-detection'
}
function Invoke-CourseUv {
    param([string[]]$UvArguments)
    $uvCommand = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvCommand) {
        & $uvCommand.Source @UvArguments
    } else {
        & python -m uv @UvArguments
    }
    if ($LASTEXITCODE -ne 0) { throw 'uv failed. Read the preceding error message.' }
}
$moduleRoot = Join-Path $PSScriptRoot $modulePaths[$Module]
$notebookRoot = Join-Path $moduleRoot 'notebooks'
if ($Language -eq 'zh-CN') {
    if ($Module -ne 'detection') { throw 'Only detection shares its environment across language editions.' }
    $notebookRoot = Join-Path (Split-Path $PSScriptRoot -Parent) '02-object-detection/notebooks'
}
if ($DryRun) {
    [pscustomobject]@{
        Language = $Language
        Module = $Module
        ModuleRoot = $moduleRoot
        WorkingDirectory = $moduleRoot
        NotebookRoot = $notebookRoot
    }
    return
}
Push-Location $moduleRoot
try {
    Invoke-CourseUv -UvArguments @('sync', '--locked', '--default-index', 'https://pypi.org/simple')
    Invoke-CourseUv -UvArguments @('run', '--locked', '--default-index', 'https://pypi.org/simple', 'jupyter', 'lab', '--notebook-dir', $notebookRoot)
} finally {
    Pop-Location
}
