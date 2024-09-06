#!/bin/bash

# Check and install Polarion Copilot packages
are_packages_installed() {
    while read -r line
    do
      package_list+=$line
    done < "$1"
    echo "$package_list"
    return 0
}