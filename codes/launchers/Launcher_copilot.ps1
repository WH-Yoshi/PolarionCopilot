$embed_port = 22027
$mistral_port = 22028

$embed_remote_port = 22016
$mistral_remote_port = 22002

$address_embed = "northcarolina-b.tensordockmarketplace.com"
$address_mistral = "idaho-b.tensordockmarketplace.com"

$ssh_embedding = "ssh -N -f -p $embed_remote_port user@$address_embed -i ~\.ssh\id_rsa_tensordock -L 22027:localhost:8080 2>`$null"
$ssh_mistral = "ssh -N -f -p $mistral_remote_port user@$address_mistral -i ~\.ssh\id_rsa_tensordock -L 22028:localhost:8000 2>`$null"

function exec_ssh($SSH_COMMAND) {
    Start-Process -FilePath "powershell" -ArgumentList "-Command", $SSH_COMMAND -NoNewWindow
}

function message($port){
    Write-Host "Port $port is open on localhost"
}

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

If ($MyInvocation.InvocationName -ne ".")
{
    # Check if local embedding port is open (listening)
    $embedding_PORT_STATUS = netstat -an | Select-String ":$embed_remote_port" | Select-String "ESTABLISHED"
    if (-not $embedding_PORT_STATUS)
    {
        Write-Host "Port $embed_port is closed on localhost. Running SSH command..."
        exec_ssh $ssh_embedding
    }
    else
    {
        Write-Host "Port $embed_port is open on localhost"
    }

    # Check if local mistral port is open (listening)
    $mistral_PORT_STATUS = netstat -an | Select-String ":$mistral_remote_port" | Select-String "ESTABLISHED"
    if (-not $mistral_PORT_STATUS)
    {
        Write-Host "Port $mistral_port is closed on localhost. Running SSH command..."
        exec_ssh $ssh_mistral
    }
    else
    {
        Write-Host "Port $mistral_port is open on localhost"
    }

    # Verify remote connections
    $embedding_STATUS = Get-NetTCPConnection -State Established -RemotePort $embed_remote_port 2> $null
    $mistral_STATUS = Get-NetTCPConnection -State Established -RemotePort $mistral_remote_port 2> $null

    if ($embedding_STATUS -and $mistral_STATUS)
    {
        Write-Host "[SSH TUNNEL OK]" -ForegroundColor Green
        python .\codes\before_code.py
        python .\codes\Copilot.py
    }
    else
    {
        Write-Host "Execution of one or both SSH tunnel was unsuccessful." -ForegroundColor Red
        Write-Host "`nPlease check the Remote Virtual Machines. They must be running to use the APP! " -ForegroundColor Yellow
        Write-Host "Follow these instruction for the deployment of the cloud GPU via TensorDock." -ForegroundColor Yellow
        Write-Host "https://gitlab.sw.goiba.net/req-test-tools/polarion-copilot/copilot-proto#polarioncopilot`n" -ForegroundColor Cyan
    }
}