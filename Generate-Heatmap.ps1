$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js belum terinstal. Instal Node.js 18 atau lebih baru."
}

if (-not $env:GH_USERNAME) {
    $env:GH_USERNAME = "muhrafi-fsdev"
}

$temporaryToken = $false
if (-not $env:GH_TOKEN) {
    Write-Host "Masukkan GitHub PAT dengan izin minimum read:user dan public_repo." -ForegroundColor Yellow
    $secureToken = Read-Host "GitHub PAT" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $env:GH_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        $temporaryToken = $true
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

try {
    npm install
    npm run generate
    Write-Host "`nHeatmap dark/light berhasil dibuat di assets\heatmap." -ForegroundColor Green

    if (Test-Path ".git") {
        $answer = Read-Host "Commit dan push hasil heatmap sekarang? (Y/N)"
        if ($answer -match "^[Yy]") {
            git add assets/heatmap/dark.svg assets/heatmap/light.svg
            git commit -m "Update animated contribution heatmap"
            git push origin main
        }
    }
}
finally {
    if ($temporaryToken) {
        Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue
    }
}
