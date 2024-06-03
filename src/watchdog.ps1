$targetServiceName = "WatchAgentService"

function CheckAndSetStartupType {
    Write-Host "Checking startup type of $targetServiceName..."
    $service = Get-WmiObject -Class Win32_Service -Filter "Name='$targetServiceName'"
    Write-Host "Service StartMode: $($service.StartMode)"
    if ($service.StartMode -ne "Auto") {
        Write-Host "Changing startup type of $targetServiceName to Automatic."
        $service.ChangeStartMode("Automatic")
        Write-Host "Startup type changed."
    } else {
        Write-Host "Startup type is already Automatic."
    }
}

while ($true) {
    CheckAndSetStartupType
    Write-Host "Sleeping for 2 seconds..."
    Start-Sleep -Seconds 2
}
