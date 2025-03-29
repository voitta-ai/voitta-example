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

# Create the development virtual environment if it doesn't exist or force flag is set
if [ ! -d ".venv-dev" ] || [ "$FORCE" = true ]; then
    if [ "$FORCE" = true ] && [ -d ".venv-dev" ]; then
        echo "Force flag set. Removing existing development virtual environment..."
        rm -rf .venv-dev
    fi
    
    echo "Creating development virtual environment..."
    python3 -m venv .venv-dev
    source .venv-dev/bin/activate
    pip install -r requirements.txt
    pip uninstall -y voitta  # Remove voitta if it was installed
fi
. .venv-dev/bin/activate


# Set PYTHONPATH to include the local voitta implementation
export PYTHONPATH="../voitta:$PYTHONPATH"

echo "Development environment activated."
echo "Using local voitta implementation from: ../voitta"
echo "PYTHONPATH: $PYTHONPATH"
