#!/bin/bash

# Check if a virtual environment is active and deactivate it
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Deactivating current virtual environment..."
    deactivate
fi

# Parse command line arguments
FORCE=false
while getopts "f" opt; do
    case $opt in
        f) FORCE=true ;;
        *) ;;
    esac
done

# Create the testing virtual environment if it doesn't exist or force flag is set
if [ ! -d ".venv-test" ] || [ "$FORCE" = true ]; then
    if [ "$FORCE" = true ] && [ -d ".venv-test" ]; then
        echo "Force flag set. Removing existing testing virtual environment..."
        rm -rf .venv-test
    fi
    
    echo "Creating testing virtual environment..."
    python -m venv .venv-test
    source .venv-test/bin/activate
    pip install -r requirements.txt
fi
source .venv-test/bin/activate


echo "Testing environment activated."
echo "Using PyPI voitta implementation."
