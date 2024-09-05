$embedding_port = 22027
$mistral_port = 22028

$embedding_remote_port = "22016"
$mistral_remote_port = "22002"

$ssh_embedding = "ssh -N -f -p $embedding_remote_port user@northcarolina-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080"
$ssh_mistral = "ssh -N -f -p $mistral_remote_port user@idaho-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000"

function exec_ssh($SSH_COMMAND) {
    Start-Process -FilePath "powershell" -ArgumentList "-Command", $SSH_COMMAND -NoNewWindow
}

# Check if embedding port is open (listening or established)
$embedding_STATUS = netstat -an | Select-String -Pattern ":$embedding_port.*LISTENING"
$embedding_STATUS = if ($embedding_STATUS) { 0 } else { 1 }

# Check if mistral port is open (listening or established)
$mistral_STATUS = netstat -an | Select-String -Pattern ":$mistral_port.*LISTENING"
$mistral_STATUS = if ($mistral_STATUS) { 0 } else { 1 }

if ($embedding_STATUS -eq 0) {
    Write-Host "Port 22027 is open on localhost. [Embedding]"
}
if ($mistral_STATUS -eq 0) {
    Write-Host "Port 22028 is open on localhost. [Mistral]"
}

# If embedding port is closed, run the SSH command for embedding port
if ($embedding_STATUS -ne 0) {
    Write-Host "Port $embedding_port is closed. Running SSH command..."
    exec_ssh $ssh_embedding
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH command for port $embedding_port applied..`n"
    } else {
        Write-Host "Error: SSH command for port $embedding_port failed with exit code $LASTEXITCODE."
        Write-Host "The remote virtual machine for port $embedding_port is probably not running."
    }
}

# If mistral port is closed, run the SSH command for mistral port
if ($mistral_STATUS -ne 0) {
    Write-Host "Port $mistral_port is closed. Running SSH command..."
    exec_ssh $ssh_mistral
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH command for port $mistral_port successful."
    } else {
        Write-Host "Error: SSH command for port $mistral_port failed with exit code $LASTEXITCODE."
        Write-Host "The remote virtual machine for port $mistral_port is probably not running."
    }
}
Write-Host "`n"

python .\codes\before_code.py
python .\codes\Copilot.py