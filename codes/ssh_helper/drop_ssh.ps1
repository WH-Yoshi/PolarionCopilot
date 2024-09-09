$scriptDir = $PSScriptRoot

. $scriptDir/../launchers/Launcher_copilot.ps1

$port_embed = return_port1
$port_mistral = return_port2
$address_embed = return_address1
$address_mistral = return_address2

$connections = Get-NetTCPConnection -State Established

$portConnection = $connections | Where-Object {
    ($_.RemotePort -eq $port_embed -or $_.RemotePort -eq $port_mistral) -and
    (($_.RemoteAddress -eq $address_embed -or $_.RemoteAddress -eq (Resolve-DnsName -Name $address_embed).IPAddress) -or
    ($_.RemoteAddress -eq $address_mistral -or $_.RemoteAddress -eq (Resolve-DnsName -Name $address_mistral).IPAddress))
}

if ($portConnection) {
    Write-Host "Active connection found."
    $portConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
    Read-Host "Do you want to delete the connection? (Enter or Ctrl+C)"
    $portConnection | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
    Write-Host "Connection deleted."
} else {
    Write-Host "No active connection found."
}