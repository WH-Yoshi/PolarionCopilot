#!/bin/bash

PORT1=22027
PORT2=22028
SSH_COMMAND_EM="ssh -N -f -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22027:localhost:8080"
SSH_COMMAND_MI="ssh -N -f -p 22002 user@idaho-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22028:localhost:8000"

check_port() {
  local PORT=$1
  if nc -zv localhost "$PORT" 2>&1 | grep -q 'succeeded'; then
    echo "Port $PORT is open on localhost"
    return 0
  else
    echo "Port $PORT is closed on localhost"
    return 1
  fi
}

check_port $PORT1
PORT1_STATUS=$?

check_port $PORT2
PORT2_STATUS=$?

if [ $PORT1_STATUS -ne 0 ] || [ $PORT2_STATUS -ne 0 ]; then
  echo "One or both ports are closed. Running SSH command..."
  $SSH_COMMAND_EM
  $SSH_COMMAND_MI
  if [ $? -eq 0 ]; then
    echo "SSH command successful."
  else
    echo "Error: SSH command failed with exit code $?."
    echo "One or both remote virtual machine are probably not running."
  fi
fi

python3 ./codes/before_code.py
python3 ./codes/Copilot.py