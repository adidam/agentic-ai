# Python Environment Cleanup and Analysis Script

Write-Host "=== Python Environment Analysis ===" -ForegroundColor Green

# Find all Python installations
Write-Host "`nFinding Python installations..." -ForegroundColor Yellow
$pythonExes = Get-ChildItem C:\ -Recurse -Name "python.exe" -ErrorAction SilentlyContinue
foreach ($exe in $pythonExes) {
    $fullPath = "C:\$exe"
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        $directory = Split-Path $fullPath -Parent
        $dirSize = (Get-ChildItem $directory -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Write-Host "Python: $fullPath"
        Write-Host "  Directory size: $([math]::Round($dirSize/1MB,2)) MB" -ForegroundColor Cyan
    }
}

# Find virtual environments
Write-Host "`nFinding virtual environments..." -ForegroundColor Yellow
$venvDirs = @()
$commonVenvNames = @("venv", "env", ".venv", ".env", "virtualenv")

foreach ($name in $commonVenvNames) {
    $dirs = Get-ChildItem C:\ -Recurse -Directory -Name $name -ErrorAction SilentlyContinue
    foreach ($dir in $dirs) {
        $fullPath = "C:\$dir"
        if (Test-Path "$fullPath\Scripts\python.exe" -or Test-Path "$fullPath\bin\python") {
            $size = (Get-ChildItem $fullPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            if ($size -gt 10MB) {
                $venvDirs += @{
                    Path = $fullPath
                    Size = $size
                    SizeMB = [math]::Round($size/1MB, 2)
                }
                Write-Host "Virtual env: $fullPath - $([math]::Round($size/1MB,2)) MB" -ForegroundColor Cyan
            }
        }
    }
}

# Find large Python packages directories
Write-Host "`nFinding large site-packages directories..." -ForegroundColor Yellow
$sitePackages = Get-ChildItem C:\ -Recurse -Directory -Name "site-packages" -ErrorAction SilentlyContinue
foreach ($pkg in $sitePackages) {
    $fullPath = "C:\$pkg"
    $size = (Get-ChildItem $fullPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($size -gt 50MB) {
        Write-Host "Large site-packages: $fullPath - $([math]::Round($size/1MB,2)) MB" -ForegroundColor Red
    }
}

# Check pip cache
Write-Host "`nChecking pip cache..." -ForegroundColor Yellow
$pipCache = "$env:LOCALAPPDATA\pip\cache"
if (Test-Path $pipCache) {
    $cacheSize = (Get-ChildItem $pipCache -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    Write-Host "Pip cache: $pipCache - $([math]::Round($cacheSize/1MB,2)) MB" -ForegroundColor Red
    Write-Host "  Run 'pip cache purge' to clear" -ForegroundColor Gray
}

# Summary
Write-Host "`n=== Summary and Recommendations ===" -ForegroundColor Green
$totalVenvSize = ($venvDirs | ForEach-Object { $_.Size } | Measure-Object -Sum).Sum
Write-Host "Total virtual environment size: $([math]::Round($totalVenvSize/1GB,2)) GB"

Write-Host "`nRecommended actions:" -ForegroundColor Yellow
Write-Host "1. Clear pip cache: pip cache purge"
Write-Host "2. Remove unused virtual environments"
Write-Host "3. Move future Python installations to D: drive"
Write-Host "4. Configure pip cache to D: drive"
Write-Host "5. Consider using conda/mamba for better space efficiency"

# Generate cleanup commands
Write-Host "`n=== Cleanup Commands ===" -ForegroundColor Green
Write-Host "# Clear pip cache"
Write-Host "pip cache purge"
Write-Host ""
Write-Host "# Configure pip to use D: drive (create %APPDATA%\pip\pip.ini):"
Write-Host "[global]"
Write-Host "cache-dir = D:\pip-cache"
Write-Host ""
Write-Host "# Remove large virtual environments (review first!):"
foreach ($venv in $venvDirs | Sort-Object Size -Descending | Select-Object -First 5) {
    Write-Host "# rmdir /s `"$($venv.Path)`"  # $($venv.SizeMB) MB"
}