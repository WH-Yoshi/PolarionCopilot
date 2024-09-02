#!/bin/bash

# Function to display active SSH connections
list_ssh_connections() {
  echo "Active SSH connections:"
  netstat -tnpa | grep 'ESTABLISHED.*ssh' | awk '{print NR, $5, $7}' | while read -r line; do
    echo "$line"
  done
}

# Function to drop a selected SSH connection
drop_ssh_connection() {
  local connection_number=$1
  local pid=$(netstat -tnpa | grep 'ESTABLISHED.*ssh' | awk "NR==$connection_number {print \$7}" | cut -d'/' -f1)
  if [ -n "$pid" ]; then
    kill -9 "$pid"
    echo "Connection $connection_number dropped."
  else
    echo "Invalid selection."
  fi
}

# Main script
list_ssh_connections
echo "Enter the number of the connection you want to drop (or 'q' to quit):"
read -r selection

if [ "$selection" != "q" ]; then
  drop_ssh_connection "$selection"
fi