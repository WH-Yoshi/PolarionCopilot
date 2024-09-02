#!/bin/bash

PORT1=22027
PORT2=22028
SSH_COMMAND="ssh -N -f -p 22002 user@idaho-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22028:localhost:8000"

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
  echo "One or both ports are closed. Running SSH command in a new terminal..."
  gnome-terminal -- bash -c "$SSH_COMMAND; exec bash"
  if [ $? -eq 0 ]; then
    echo "SSH command successful. Leave the terminal open."
  else
    echo "Error: SSH command failed with exit code $?."
  fi
fi

python3 ./codes/before_code.py
python3 ./codes/Copilot.py