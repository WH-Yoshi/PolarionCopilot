# Demander à l'utilisateur de saisir le port et l'adresse
$portToCheck = Read-Host "Remote Port: "
$addressToCheck = Read-Host "Remote IPv4 Address or Domain: "

# Obtenir toutes les connexions TCP actives
$connections = Get-NetTCPConnection -State Established

# Filtrer les connexions utilisant le port et l'adresse spécifiés
$portConnection = $connections | Where-Object {
    $_.RemotePort -eq $portToCheck -and
    ($_.RemoteAddress -eq $addressToCheck -or $_.RemoteAddress -eq (Resolve-DnsName -Name $addressToCheck).IPAddress)
}

if ($portConnection) {
    # Si une connexion est trouvée, afficher les détails
    Write-Host "Active connection found."
    $portConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
    Write-Host "Deleting connection..."
    # Supprimer la connexion
    $portConnection | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
} else {
    Write-Host "No active connection found."
}