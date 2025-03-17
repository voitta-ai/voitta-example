#!/bin/bash

# Create the development virtual environment if it doesn't exist
if [ ! -d ".venv-dev" ]; then
    echo "Creating development virtual environment..."
    python -m venv .venv-dev
    source .venv-dev/bin/activate
    pip install -r requirements.txt
    pip uninstall -y voitta  # Remove voitta if it was installed
else
    source .venv-dev/bin/activate
fi

# Set PYTHONPATH to include the local voitta implementation
export PYTHONPATH="../voitta:$PYTHONPATH"

echo "Development environment activated."
echo "Using local voitta implementation from: ../voitta"
echo "PYTHONPATH: $PYTHONPATH"
