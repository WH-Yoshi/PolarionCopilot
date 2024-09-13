#!/bin/bash

address_embed="northcarolina-b.tensordockmarketplace.com"
embed_remote_port=22016
address_mistral="idaho-b.tensordockmarketplace.com"
mistral_remote_port=22002

ssh_key_path="~/.ssh/id_rsa_tensordock"

ssh_embedding="ssh -N -p $embed_remote_port user@$address_embed -i $ssh_key_path -L 22027:localhost:8080"
ssh_mistral="ssh -N -p $mistral_remote_port user@$address_mistral -i $ssh_key_path -L 22028:localhost:8000"

interval=60

check_ssh() {
  # Check if SSH tunnel is up. If yes he will print the tunnel is up.
  #   If not --> Check if the remote server can accept an ssh tunnel.
  #     If yes --> Start the tunnel
  #     If not --> Server is down

    local address=$1
    local remote_port=$2
    local ssh_command=$3
    local local_port=$4
    echo ""
    echo "Verifying SSH on $address:$remote_port..."

    if netstat -tnpa | grep 'ESTABLISHED.*ssh' | grep "$remote_port" > /dev/null 2>&1; then
        echo -e "\e[32m   ↳ SSH tunnel up on $address localport : $local_port.\e[0m"
    else
        if nc -z -w 3 "$address" "$remote_port"; then
            echo "↳ SSH Tunnel is available on $address. Opening SSH Tunnel..."
            nohup "$ssh_command" &>/dev/null &
            echo -e "\e[32m   ↳ SSH tunnel up on $address localport : $local_port.\e[0m"
        else
            echo -e "\e[31m Tensordock VM : [$address] is probably down\e[0m"
        fi
    fi
}

while true; do
    check_ssh "$address_embed" "$embed_remote_port" "$ssh_embedding" 22027
    check_ssh "$address_mistral" "$mistral_remote_port" "$ssh_mistral" 22028
    sleep "$interval"
done