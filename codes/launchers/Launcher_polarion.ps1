$PORT = 22027
$SSH_COMMAND = 'ssh -N -f -p 41708 user@91.150.160.37 -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080'

# Vérifier si le PORT est ouvert (en écoute ou établi)
$PORT_STATUS = netstat -an | Select-String -Pattern ":$PORT.*LISTENING"
if ($PORT_STATUS) {
    Write-Host "Port $PORT is open on localhost"
} else {
    Write-Host "Port $PORT is closed on localhost. Running SSH command..."
    Invoke-Expression $SSH_COMMAND
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH command successful."
    } else {
        Write-Host "Error: SSH command failed with exit code $LASTEXITCODE."
        Write-Host "The remote virtual machine is probably not running."
    }
}

python .\codes\before_code.py
python .\codes\Polarion.py
