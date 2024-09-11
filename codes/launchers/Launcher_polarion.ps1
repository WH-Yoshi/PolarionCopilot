$PORT = 22027
$REMOTE_PORT = 22016

# Check if local port is open (listening)
$PORT_STATUS = netstat -an | Select-String ":$PORT" | Select-String "LISTEN"
if (-not $PORT_STATUS) {
    Write-Host "Port $PORT is closed on localhost. Running SSH command..."
    Start-Process ssh -ArgumentList "-N -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080" -NoNewWindow
}
else {
    Write-Host "Port $PORT is open on localhost"
    Write-Host "[SSH TUNNEL OK]" -ForegroundColor Green
    exit
}

# Initialize remote status variable
$REMOTE_STATUS = $null

# Verify remote connection
for ($i = 0; $i -lt 3; $i++) {
    $REMOTE_STATUS = Get-NetTCPConnection -State Established -RemotePort $REMOTE_PORT -ErrorAction SilentlyContinue
    if ($REMOTE_STATUS) {
        Write-Host "Remote machine is up and running."
        break
    }
    else {
        Write-Host "Remote machine is down, retrying in 2 seconds..."
        Start-Sleep -Seconds 2
    }
}

if (-not $REMOTE_STATUS) {
    Write-Host "Remote machine is down, workitems will be saved locally for later."
}

# Run Python scripts
python .\codes\before_code.py
python .\codes\Polarion.py
