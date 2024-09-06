#!/bin/bash

# Check and install Polarion Copilot packages
are_packages_installed() {
    file_path="./requirements.txt"
    while read -r line
    do
      package_list+=$line
    done < "$file_path"
    echo "$package_list"
    return 0
}

install_packages() {
    file_path="./requirements.txt"
    while read line
    do
      package_list+=$line
    done < "$file_path"
    echo "$package_list"
    return 0
}

# Check if the required packages are installed
if are_packages_installed; then
    echo "All required packages are installed"
else
    echo "Installing required packages"
    if install_packages; then
        echo "Packages installed successfully"
    else
        echo "Failed to install packages"
    fi
fi