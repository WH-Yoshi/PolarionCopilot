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
}

# Verify remote connection
$REMOTE_STATUS = Get-NetTCPConnection -State Established -RemotePort $REMOTE_PORT 2> $null

if ($REMOTE_STATUS) {
    Write-Host "[SSH TUNNEL OK]" -ForegroundColor Green
    python .\codes\before_code.py
    python .\codes\Polarion.py
} else {
    Write-Host "Please check the Embedding Virtual Machine. It must be running to use the APP!" -ForegroundColor Red
    Write-Host "Follow these instructions for the deployment of the cloud GPU via TensorDock." -ForegroundColor Yellow
    Write-Host "https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto#polarioncopilot`n" -ForegroundColor Cyan
}