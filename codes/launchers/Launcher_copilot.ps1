$embed_port = 22027
$mistral_port = 22028
$embed_remote_port = 22016
$mistral_remote_port = 22002

function return_port1(){
    return $embed_remote_port
}

function return_port2(){
    return $mistral_remote_port
}

function return_address1(){
    return $address_embed
}

function return_address2(){
    return $address_mistral
}

$address_embed = "northcarolina-b.tensordockmarketplace.com"
$address_mistral = "idaho-b.tensordockmarketplace.com"

$ssh_embedding = "-N -p $embed_remote_port user@$address_embed -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080"
$ssh_mistral = "-N -p $mistral_remote_port user@$address_mistral -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000"

function exec_ssh($SSH_COMMAND) {
    Start-Process ssh -ArgumentList $SSH_COMMAND -NoNewWindow
}

function message($port){
    Write-Host "Port $port is open on localhost"
}

If ($MyInvocation.InvocationName -ne ".")
{
    # Check if local embedding port is open (listening)
    $embedding_PORT_STATUS = netstat -an | Select-String ":$embed_remote_port" | Select-String "LISTEN"
    if (-not $embedding_PORT_STATUS)
    {
        Write-Host "Port $embed_port is closed on localhost. Running SSH command..."
        exec_ssh $ssh_embedding
    }
    else
    {
        message($embed_port)
    }

    # Check if local mistral port is open (listening)
    $mistral_PORT_STATUS = netstat -an | Select-String ":$mistral_remote_port" | Select-String "LISTEN"
    if (-not $mistral_PORT_STATUS) {
        Write-Host "Port $mistral_port is closed on localhost. Running SSH command..."
        exec_ssh $ssh_mistral
    }
    else {
        message($mistral_port)
    }

    for ($i = 0; $i -lt 3; $i++) {
        $embedding_STATUS = Get-NetTCPConnection -State Established -RemotePort $embed_remote_port -ErrorAction SilentlyContinue
        $mistral_STATUS = Get-NetTCPConnection -State Established -RemotePort $mistral_remote_port -ErrorAction SilentlyContinue
        if ($embedding_STATUS -and $mistral_STATUS) {
            Write-Host "[SSH TUNNEL OK]" -ForegroundColor Green
            break
        }
        else {
            Write-Host "Remote machine is down, retrying in 2 seconds..."
            Start-Sleep -Seconds 2
        }
    }

    if (-not $embedding_STATUS -or -not $mistral_STATUS) {
        Write-Host "Remote machine is down. Exiting..."
        exit
    }

    # Run Python scripts
    python .\codes\before_code.py
    python .\codes\CoPilot.py
}