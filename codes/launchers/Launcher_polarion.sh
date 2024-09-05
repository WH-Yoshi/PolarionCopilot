#!/bin/bash

PORT=22027
SSH_COMMAND="ssh -N -f -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22027:localhost:8080"

if nc -zv localhost "$PORT" 2>&1 | grep -q 'succeeded'; then
  echo "Port $PORT is open on localhost"
else
  echo "Port $PORT is closed on localhost. Opening SSH tunnel..."
  $SSH_COMMAND
  if [ $? -eq 0 ]; then
    echo "SSH command successful."
  else
    echo "Error: SSH command failed with exit code $?."
    echo "The remote virtual machine is probably not running."
  fi
fi

python3 ./codes/before_code.py
python3 ./codes/Polarion.py