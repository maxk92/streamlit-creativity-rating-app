#!/bin/bash
# Simple script to run the Streamlit app

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the Streamlit app
echo "Starting Creativity Rating App..."
streamlit run app.py
