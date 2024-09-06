$embedding_port = 22027
$mistral_port = 22028

$embedding_remote_port = "22016"
$mistral_remote_port = "22002"

$ssh_embedding = "ssh -N -f -p $embedding_remote_port user@northcarolina-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080 2>`$null"
$ssh_mistral = "ssh -N -f -p $mistral_remote_port user@idaho-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000 2>`$null"

function exec_ssh($SSH_COMMAND) {
    Start-Process -FilePath "powershell" -ArgumentList "-Command", $SSH_COMMAND -NoNewWindow
}

function message($port){
    Write-Host "[SSH TUNNEL] " -ForegroundColor Green -NoNewline
    Write-Host "Port $port is open on localhost"
}

# Check if local embedding port is open (listening)
$embedding_PORT_STATUS = netstat -an | Select-String -Pattern ":$embedding_port.*LISTENING"
if (-not $embedding_PORT_STATUS) {
    Write-Host "Port $embedding_port is closed on localhost. Running SSH command..."
    exec_ssh $ssh_embedding
}

# Check if local mistral port is open (listening)
$mistral_PORT_STATUS = netstat -an | Select-String -Pattern ":$mistral_port.*LISTENING"
if (-not $mistral_PORT_STATUS) {
    Write-Host "Port $mistral_port is closed on localhost. Running SSH command..."
    exec_ssh $ssh_mistral
}

# Verify remote connections
$embedding_STATUS = Get-NetTCPConnection -State Established -RemotePort $embedding_remote_port 2>`$null
$mistral_STATUS = Get-NetTCPConnection -State Established -RemotePort $mistral_remote_port 2>`$null

if ($embedding_STATUS -and $mistral_STATUS) {
    message($embedding_port)
    message($mistral_port)
    python .\codes\before_code.py
    python .\codes\Polarion.py
} else {
    Write-Host "Execution of one or both SSH tunnel was unsuccessful." -ForegroundColor Red
    Write-Host "`nPlease check the Remote Virtual Machine. They must be running to use the APP!" -ForegroundColor Yellow
    Write-Host "Follow these instruction for the deployment of the cloud GPU via TensorDock." -ForegroundColor Yellow
    Write-Host "https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto#polarioncopilot`n" -ForegroundColor Blue
}