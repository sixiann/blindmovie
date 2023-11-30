#!/bin/bash

# Define the name of the virtual environment
VENV_NAME="myenv"

# Create a virtual environment
python3 -m venv $VENV_NAME

# Activate the virtual environment
source $VENV_NAME/bin/activate

# Check if requirements.txt exists and then install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found"
fi
