#!/bin/bash

# Update package list
sudo apt-get update

# Install Java (required for PySpark)
sudo apt-get install -y default-jdk

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete! You can now run the app using: streamlit run streamlit_app.py"
