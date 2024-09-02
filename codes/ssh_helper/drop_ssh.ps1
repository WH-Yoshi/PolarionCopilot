# Function to display active SSH connections
function List-SshConnections
{
    Write-Output "Active SSH connections:"
    netstat -anop tcp | Select-String 'ESTABLISHED.*ssh' | ForEach-Object {
        $fields = $_ -split '\s+'
        $index = [array]::IndexOf($fields, 'ESTABLISHED')
        $remoteAddress = $fields[$index - 1]
        $pid = $fields[$index + 1] -split '/' | Select-Object -First 1
        Write-Output "$( $fields[0] ) $remoteAddress $pid"
    }
}

# Function to drop a selected SSH connection
function Drop-SshConnection {
    param (
        [int]$ConnectionNumber
    )
    $connection = netstat -anop tcp | Select-String 'ESTABLISHED.*ssh' | Select-Object -Index ($ConnectionNumber - 1)
    if ($connection) {
        $fields = $connection -split '\s+'
        $index = [array]::IndexOf($fields, 'ESTABLISHED')
        $pid = $fields[$index + 1] -split '/' | Select-Object -First 1
        Stop-Process -Id $pid -Force
        Write-Output "Connection $ConnectionNumber dropped."
    } else {
        Write-Output "Invalid selection."
    }
}

# Main script
List-SshConnections
$selection = Read-Host "Enter the number of the connection you want to drop (or 'q' to quit)"

if ($selection -ne 'q') {
    Drop-SshConnection -ConnectionNumber [int]$selection
}