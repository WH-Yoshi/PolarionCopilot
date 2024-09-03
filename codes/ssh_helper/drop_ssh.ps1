# Define the port you want to check
$portToCheck = 41708
$addressToCheck = "91.150.160.37"

# Get all active TCP connections
$connections = Get-NetTCPConnection -State Established

# Filter for connections using the specified local port
$portConnection = $connections | Where-Object { $_.RemotePort -eq $portToCheck } | Where-Object { $_.RemoteAddress -eq $addressToCheck }

if ($portConnection) {
    # If a connection is found, display details
    Write-Host "Active connection found"
    $portConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
} else {
    Write-Host "No active connection found"
}
