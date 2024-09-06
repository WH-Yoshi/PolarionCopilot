#!/bin/bash

# Check if the requirements.txt file exists
if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found!"
    exit 1
fi

# Check if each package from the requirements.txt is installed
while IFS= read -r package; do
    # Strip version constraints if present
    pkg_name=$(echo "$package" | cut -d '=' -f 1)

    # Check if the package is installed
    pip show "$pkg_name" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "$pkg_name is not installed."
    fi
done < requirements.txt

echo "Check complete."
