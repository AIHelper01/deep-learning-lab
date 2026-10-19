# The repository root is the Chinese course root (the masters), so the root
# launcher defaults to -Language zh-CN; the english/ shim keeps 'en'.
param(
    [ValidateSet('en', 'zh-CN')]
    [string]$Language = 'zh-CN',
    [ValidateSet('vision', 'pytorch', 'paddle', 'detection')]
    [string]$Module = 'vision',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'

# One uv project for the whole course: this repository root. Both language
# editions share the root .venv, so `uv sync` once and every module runs.
$modulePaths = @{
    vision = '01-image-classification'
    pytorch = '03-sentiment-analysis/pytorch'
    paddle = '03-sentiment-analysis/paddle'
    detection = '02-object-detection'
}
$sideRoot = if ($Language -eq 'en') { Join-Path $PSScriptRoot 'english' } else { $PSScriptRoot }
$moduleRoot = Join-Path $sideRoot $modulePaths[$Module]
$notebookRoot = Join-Path $moduleRoot 'notebooks'

if ($DryRun) {
    [pscustomobject]@{
        Language = $Language
        Module = $Module
        ModuleRoot = $moduleRoot
        WorkingDirectory = $notebookRoot
        NotebookRoot = $notebookRoot
        ProjectRoot = $PSScriptRoot
    }
    return
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

if (-not (Test-Path -LiteralPath $notebookRoot -PathType Container)) {
    throw "No notebooks at $notebookRoot. Check -Language and -Module."
}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'uv.lock') -PathType Leaf)) {
    throw 'Missing uv.lock in the repository root. Restore it with git checkout, see docs/environment-setup.md.'
}

# uv resolves the project from the current directory, so run from the repository root.
Push-Location $PSScriptRoot
try {
    Invoke-CourseUv -UvArguments @('sync', '--locked', '--default-index', 'https://pypi.org/simple')
    Invoke-CourseUv -UvArguments @('run', '--locked', '--default-index', 'https://pypi.org/simple', 'jupyter', 'lab', '--notebook-dir', $notebookRoot)
} finally {
    Pop-Location
}
