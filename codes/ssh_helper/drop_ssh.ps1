# Define the port you want to check
$portToCheck = 22027

# Get all active TCP connections
$connections = Get-NetTCPConnection -State Established

# Filter for connections using the specified local port
$portConnection = $connections | Where-Object { $_.LocalPort -eq $portToCheck }

if ($portConnection) {
    # If a connection is found, display details
    Write-Host "Active connection found on local port $portToCheck"
    $portConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
} else {
    Write-Host "No active connection found on local port $portToCheck"
}
