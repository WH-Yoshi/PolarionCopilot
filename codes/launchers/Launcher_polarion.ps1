$PORT = 22027
$REMOTE_PORT = 47939

$SSH_COMMAND = "ssh -N -f -p $REMOTE_PORT user@213.180.0.77 -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080"

# Vérifier si le PORT est ouvert (en écoute ou établi)
$PORT_STATUS = netstat -an | Select-String -Pattern ":$PORT.*LISTENING"
if ($PORT_STATUS) {
    Write-Host "Port $PORT is open on localhost"
} else {
    Write-Host "Port $PORT is closed on localhost. Running SSH command in a new terminal..."
    Start-Process -FilePath "powershell" -ArgumentList "-Command", $SSH_COMMAND -NoNewWindow
}

python .\codes\before_code.py
python .\codes\Polarion.py
