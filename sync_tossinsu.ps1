# sync_tossinsu.ps1 - tossinsu auto sync script
# Usage: .\sync_tossinsu.ps1 "commit message"
# Effect: git add + commit + push (one shot) for tossinsu repo
# Location: place at C:\dev\projects\tossinsu\sync_tossinsu.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

# Default message if not provided
if ([string]::IsNullOrWhiteSpace($Message)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    $Message = "sync: $timestamp"
}

Write-Host ""
Write-Host "=== sync_tossinsu.ps1 ===" -ForegroundColor Cyan
Write-Host "Commit message: $Message" -ForegroundColor Yellow
Write-Host ""

# Step 1: git status check
Write-Host "[1/4] Checking changes..." -ForegroundColor Green
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "  No changes detected. Exiting." -ForegroundColor Yellow
    exit 0
}
Write-Host "  Changes found:"
git status --short
Write-Host ""

# Step 2: git add
Write-Host "[2/4] Staging files..." -ForegroundColor Green
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: git add failed" -ForegroundColor Red
    exit 1
}
Write-Host "  OK" -ForegroundColor Green
Write-Host ""

# Step 3: git commit
Write-Host "[3/4] Committing..." -ForegroundColor Green
git commit -m "$Message"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: git commit failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: git push
Write-Host "[4/4] Pushing to GitHub..." -ForegroundColor Green
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: git push failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "=== Sync completed successfully ===" -ForegroundColor Cyan
Write-Host "URL: https://2309006.github.io/tossinsu/" -ForegroundColor Cyan
Write-Host ""
