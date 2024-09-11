#!/bin/bash

cd "$(dirname "${0}")/../.." || exit 1

PORT=22027
SSH_COMMAND="ssh -N -f -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L $PORT:localhost:8080"

echo -e "\e[96mChecking SSH connection...\e[0m"

if nc -zv localhost "$PORT" 2>&1 | grep -q 'succeeded'; then
  echo -e "\e[32mPort to Embedding machine: $PORT is open on localhost\e[0m"
else
  echo -e "\e[33mPort to Embedding machine: $PORT is closed on localhost. Opening SSH tunnel...\e[0m"
  $SSH_COMMAND
  if [ $? -eq 0 ]; then
    echo -e "\e[32mSSH command successful.\e[0m"
  else
    echo "Error: SSH command failed with exit code $?."
    echo -e "\e[33mRemote machine is down, workitems will be saved locally for later.\e[0m"
  fi
fi

echo -e "\e[96mChecking the environment\e[0m"
python3 -m venv .venv
source .venv/bin/activate
echo -e "\e[96mInstalling the requirements\e[0m"
pip install -r ./requirements.txt -q
python3 ./codes/before_code.py
python3 ./codes/Polarion.py