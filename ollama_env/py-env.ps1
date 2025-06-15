# Find Python executables
Get-ChildItem C:\ -Recurse -Name "python.exe" -ErrorAction SilentlyContinue | ForEach-Object {
    $size = (Get-Item "C:\$_").Length
    "C:\$_ - $([math]::Round($size/1MB,2)) MB"
}

# Find virtual environments
Get-ChildItem C:\ -Recurse -Directory -Name "*venv*" -ErrorAction SilentlyContinue
Get-ChildItem C:\ -Recurse -Directory -Name "*env*" -ErrorAction SilentlyContinue