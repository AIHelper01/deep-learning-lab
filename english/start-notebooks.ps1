# Compatibility shim: the environment now lives in the repository root, so this
# legacy entry point forwards to the root launcher with -Language en.
param(
    [ValidateSet('paddle', 'pytorch', 'vision', 'detection')]
    [string]$Module = 'vision',
    [ValidateSet('en', 'zh-CN')]
    [string]$Language = 'en',
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
& (Join-Path (Split-Path $PSScriptRoot -Parent) 'start-notebooks.ps1') -Language $Language -Module $Module -DryRun:$DryRun
