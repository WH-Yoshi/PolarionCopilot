#!/bin/bash

cd "$(dirname "${0}")/../.." || exit 1

PORT1=22027
PORT2=22028
SSH_COMMAND_EM="ssh -N -f -p 22016 user@northcarolina-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22027:localhost:8080"
SSH_COMMAND_MI="ssh -N -f -p 22002 user@idaho-b.tensordockmarketplace.com -i ~/.ssh/id_rsa_tensordock -L 22028:localhost:8000"

check_port() {
  local PORT=$1
  local DEST=$2
  if nc -zv localhost "$PORT" 2>&1 | grep -q 'succeeded'; then
    echo -e "\e[32mPort to $DEST: $PORT is open on localhost\e[0m"
    return 0
  else
    echo -e "\e[33mPort to $DEST: $PORT is closed on localhost\e[0m"
    return 1
  fi
}

echo -e "\e[96mChecking SSH connections...\e[0m"

check_port $PORT1 "Embedding Machine"
PORT1_STATUS=$?

check_port $PORT2 "Mistral Inference"
PORT2_STATUS=$?

if [ $PORT1_STATUS -ne 0 ]; then
  echo "Embedding machine connection closed. Running SSH command..."
  $SSH_COMMAND_EM
  if [ $? -eq 0 ]; then
    echo "SSH to Embedding Machine established."
  else
    echo "Error: SSH command failed with exit code $?."
    echo "Run that machine to establish the connection."
  fi
fi

if [ $PORT2_STATUS -ne 0 ]; then
  echo "Mistral Inference connection closed. Running SSH command..."
  $SSH_COMMAND_MI
  if [ $? -eq 0 ]; then
    echo "SSH to Mistral Inference established."
  else
    echo "Error: SSH command failed with exit code $?."
    echo "Run that machine to establish the connection."
  fi
fi

if [ $PORT1_STATUS -ne 0 ] || [ $PORT2_STATUS -ne 0 ]; then
  echo -e "\e[31mPlease run this script again after running the machines.\e[0m"
else
  echo -e "\e[32mAll SSH connections are established.\e[0m"
fi

echo -e "\e[96mChecking the environment...\e[0m"
python3 -m venv .venv
source .venv/bin/activate
echo -e "\e[96mInstalling the requirements...\e[0m"
pip install -r ./requirements.txt -q
echo ""
echo -e "\e[92mUse the command 'screen -r Copilot' to attach to the app.\e[0m"
echo -e "\e[92mTo detach use Ctrl + A > D \e[0m"
screen -dmS Copilot bash -c 'python3 ./codes/before_code.py; python3 ./codes/Copilot.py; exec bash'