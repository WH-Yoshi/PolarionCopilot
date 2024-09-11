#!/bin/bash

cd "$(dirname "${0}")/../.." || exit 1

PORT=22027
SSH_COMMAND="ssh -N -f -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L $PORT:localhost:8080"

if nc -zv localhost "$PORT" 2>&1 | grep -q 'succeeded'; then
  echo "\e[32mPort to Embedding machine: $PORT is open on localhost\e[0m"
else
  echo "\e[33mPort to Embedding machine: $PORT is closed on localhost. Opening SSH tunnel...\e[0m"
  $SSH_COMMAND
  if [ $? -eq 0 ]; then
    echo "\e[32mSSH command successful.\e[0m"
  else
    echo "Error: SSH command failed with exit code $?."
    echo "\e[33mRemote machine is down, workitems will be saved locally for later.\e[0m"
  fi
fi

python3 -m venv .venv
source .venv/bin/activate
pip install -r ./requirements.txt -q
python3 ./codes/before_code.py
python3 ./codes/Polarion.py