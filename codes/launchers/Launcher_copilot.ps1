$PORT1 = 22027
$PORT2 = 22028
$SSH_COMMAND = 'ssh -N -f -p 22002 user@idaho-b.tensordockmarketplace.com -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000'

# Check if PORT1 is open (listening or established)
$PORT1_STATUS = netstat -an | Select-String -Pattern ":$PORT1.*LISTENING"
$PORT1_STATUS = if ($PORT1_STATUS) { 0 } else { 1 }

# Check if PORT2 is open (listening or established)
$PORT2_STATUS = netstat -an | Select-String -Pattern ":$PORT2.*LISTENING"
$PORT2_STATUS = if ($PORT2_STATUS) { 0 } else { 1 }

# If either port is closed, run the SSH command
if ($PORT1_STATUS -ne 0 -or $PORT2_STATUS -ne 0) {
    Invoke-Expression $SSH_COMMAND
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH command successful."
    } else {
        Write-Host "Error: SSH command failed with exit code $LASTEXITCODE."
        Write-Host "One or both remote virtual machine are probably not running."
    }
}

python .\codes\before_code.py
python .\codes\Copilot.py
