$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$owner = "muhrafi-fsdev"
$repoName = "muhrafi-fsdev"
$repoFull = "$owner/$repoName"

foreach ($command in @("git", "gh")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command belum terinstal atau belum tersedia di PATH."
    }
}

gh auth status
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI belum login. Jalankan: gh auth login"
}

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

git add README.md assets generate.mjs package.json Generate-Heatmap.ps1 Setup-GitHub-Profile.ps1 .gitignore
git commit -m "Create premium animated GitHub profile"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tidak ada perubahan baru untuk di-commit atau commit gagal." -ForegroundColor Yellow
}

$repoExists = $true
gh repo view $repoFull *> $null
if ($LASTEXITCODE -ne 0) { $repoExists = $false }

if (-not $repoExists) {
    gh repo create $repoFull --public --description "Personal GitHub profile of Muhammad Rafi Priyo" --source . --remote origin --push
}
else {
    if (-not (git remote | Select-String -SimpleMatch "origin")) {
        git remote add origin "https://github.com/$repoFull.git"
    }
    git push -u origin main
}

Write-Host "`nProfil GitHub berhasil dipublikasikan." -ForegroundColor Green
Write-Host "https://github.com/$owner"
Start-Process "https://github.com/$owner"
