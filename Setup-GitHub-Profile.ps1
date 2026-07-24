$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$owner = "muhrafi-fsdev"
$repoName = "muhrafi-fsdev"
$repoFull = "$owner/$repoName"
$repoUrl = "https://github.com/$repoFull.git"

Write-Host "`nGitHub Profile Setup" -ForegroundColor Cyan
Write-Host "Repository target: $repoFull" -ForegroundColor DarkCyan

foreach ($command in @("git", "gh")) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "$command belum terinstal atau belum tersedia di PATH."
    }
}

Write-Host "`n[1/5] Memeriksa autentikasi GitHub CLI..." -ForegroundColor Cyan
& gh auth status
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI belum login. Jalankan: gh auth login"
}

Write-Host "`n[2/5] Menyiapkan repository Git lokal..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
    & git init
    if ($LASTEXITCODE -ne 0) { throw "Gagal menjalankan git init." }
}

& git branch -M main
if ($LASTEXITCODE -ne 0) { throw "Gagal menetapkan branch main." }

$filesToStage = @(
    "README.md",
    "assets",
    "generate.mjs",
    "package.json",
    "Generate-Heatmap.ps1",
    "Setup-GitHub-Profile.ps1",
    ".gitignore"
)

& git add -- $filesToStage
if ($LASTEXITCODE -ne 0) { throw "Gagal menambahkan file ke staging Git." }

$pendingChanges = & git status --porcelain
if ($pendingChanges) {
    & git commit -m "Create premium animated GitHub profile"
    if ($LASTEXITCODE -ne 0) { throw "Gagal membuat commit Git." }
}
else {
    Write-Host "Tidak ada perubahan baru yang perlu di-commit." -ForegroundColor Yellow
}

Write-Host "`n[3/5] Memeriksa repository GitHub..." -ForegroundColor Cyan
$repoExists = $false
try {
    & gh repo view $repoFull --json nameWithOwner 2>$null | Out-Null
    $repoExists = ($LASTEXITCODE -eq 0)
}
catch {
    # Repository profil belum ada. Ini kondisi normal pada setup pertama.
    $repoExists = $false
}

Write-Host "`n[4/5] Mempublikasikan profile README..." -ForegroundColor Cyan
if (-not $repoExists) {
    Write-Host "Repository belum ada. Membuat $repoFull..." -ForegroundColor Yellow

    & gh repo create $repoFull `
        --public `
        --description "Personal GitHub profile of Muhammad Rafi Priyo" `
        --source "." `
        --remote "origin" `
        --push

    if ($LASTEXITCODE -ne 0) {
        throw "Gagal membuat atau mengunggah repository profil GitHub."
    }
}
else {
    Write-Host "Repository sudah tersedia. Mengunggah perubahan terbaru..." -ForegroundColor Green

    $originExists = (& git remote) -contains "origin"
    if (-not $originExists) {
        & git remote add origin $repoUrl
        if ($LASTEXITCODE -ne 0) { throw "Gagal menambahkan remote origin." }
    }
    else {
        & git remote set-url origin $repoUrl
        if ($LASTEXITCODE -ne 0) { throw "Gagal memperbarui URL remote origin." }
    }

    & git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw "Gagal push ke branch main." }
}

Write-Host "`n[5/5] Selesai." -ForegroundColor Cyan
Write-Host "Profil GitHub berhasil dipublikasikan." -ForegroundColor Green
Write-Host "https://github.com/$owner" -ForegroundColor White

Start-Process "https://github.com/$owner"
