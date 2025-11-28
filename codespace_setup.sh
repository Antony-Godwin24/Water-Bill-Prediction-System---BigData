#!/bin/bash

# Update package list
sudo apt-get update

# Install Java (required for PySpark)
sudo apt-get install -y default-jdk

# Install Python dependencies
pip install -r requirements.txt

# Add local bin to PATH (for current session and future sessions)
export PATH=$PATH:/home/codespace/.local/bin
echo 'export PATH=$PATH:/home/codespace/.local/bin' >> ~/.bashrc

echo "Setup complete! You can now run the app using:"
echo "python -m streamlit run streamlit_app.py"
