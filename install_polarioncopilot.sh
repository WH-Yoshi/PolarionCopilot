#!/bin/bash

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "pip is not installed. Please install it first."
    exit 1
fi

# Function to install missing packages
install_missing_packages() {
    requirements=$(cat requirements.txt)
    installed_packages=$(pip list | grep -v '^#')  # Exclude comments
    missing_packages=$(echo "$installed_packages" | grep -v -F "$requirements")

    if [[ -n "$missing_packages" ]]; then
        echo "Some required packages are missing. Installing..."
        pip install -r requirements.txt
    else
        echo "All required packages are installed."
    fi
}

# Call the function
install_missing_packages