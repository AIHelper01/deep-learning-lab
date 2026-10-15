param(
    [ValidateSet('paddle', 'pytorch', 'vision', 'detection')]
    [string]$Module = 'paddle'
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
Push-Location (Join-Path $PSScriptRoot $modulePaths[$Module])
try {
    Invoke-CourseUv -UvArguments @('sync', '--locked')
    Invoke-CourseUv -UvArguments @('run', '--locked', 'jupyter', 'lab', '--notebook-dir', 'notebooks')
} finally {
    Pop-Location
}
