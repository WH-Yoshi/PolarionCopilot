#!/bin/bash

cd "$(dirname "${0}")/.." || exit 1
source codes/helpers.sh

function program_required() {
  if [ ! -x "$(command -v ${1})" ]; then
    echo "${1} is not installed on the computer..."
    if [ "${2}" ]; then
      echo "Check out this link: ${2}"
    fi
    exit 1
  fi
}

function pip_required() {
  program_required "pip" "https://pip.pypa.io/en/stable/installation/"
}

pip_required

echo "Installing Polarion Copilot..."
pip install -r requirements.txt