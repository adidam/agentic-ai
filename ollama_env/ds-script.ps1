Get-ChildItem "C:\" -Directory | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    [PSCustomObject]@{
        Name = $_.Name
        SizeGB = [math]::Round($size / 1GB, 2)
        SizeMB = [math]::Round($size / 1MB, 2)
    }
} | Sort-Object SizeGB -Descending