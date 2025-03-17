#!/bin/bash

# Create the testing virtual environment if it doesn't exist
if [ ! -d ".venv-test" ]; then
    echo "Creating testing virtual environment..."
    python -m venv .venv-test
    source .venv-test/bin/activate
    pip install -r requirements.txt
else
    source .venv-test/bin/activate
fi

echo "Testing environment activated."
echo "Using PyPI voitta implementation."
