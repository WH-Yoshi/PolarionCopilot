$PORT = 22027
$REMOTE_PORT = 22016

$SSH_COMMAND = "ssh -N -f -p $REMOTE_PORT user@northcarolina-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080 2>`$null"

function exec_ssh($SSH_COMMAND) {
    Start-Process -FilePath "powershell" -ArgumentList "-Command", $SSH_COMMAND -NoNewWindow
}

# Check if local port is open (listening)
$PORT_STATUS = netstat -an | Select-String ":$PORT" | Select-String "ESTABLISHED"
if (-not $PORT_STATUS) {
    Write-Host "Port $PORT is closed on localhost. Running SSH command..."
    exec_ssh $SSH_COMMAND
}
else
{
    Write-Host "Port $PORT is open on localhost"
    Write-Host "[SSH TUNNEL OK]" -ForegroundColor Green
}

# Verify remote connection
$REMOTE_STATUS = Get-NetTCPConnection -State Established -RemotePort $REMOTE_PORT 2> $null

if (-not $REMOTE_STATUS) {
    Write-Host "Remote machine is down, workitems will be saved locally for later."
}

python .\codes\before_code.py
python .\codes\Polarion.py
