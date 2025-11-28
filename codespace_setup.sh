#!/bin/bash

# Update package list
sudo apt-get update

# Install Java (required for PySpark)
sudo apt-get install -y default-jdk

# Install Python dependencies
pip install -r requirements.txt

# Add local bin to PATH (for current session and future sessions)
export PATH=$PATH:/home/codespace/.local/bin

# Add to .bashrc
echo 'export PATH=$PATH:/home/codespace/.local/bin' >> ~/.bashrc
# Add to .zshrc (in case zsh is used)
echo 'export PATH=$PATH:/home/codespace/.local/bin' >> ~/.zshrc
# Add to .profile (for login shells)
echo 'export PATH=$PATH:/home/codespace/.local/bin' >> ~/.profile

echo "Setup complete!"
echo "To use the 'streamlit' command directly, run this to refresh your shell:"
echo "  source ~/.bashrc  # or source ~/.zshrc"
echo ""
echo "👇 **Recommended way to run the app:** 👇"
echo "  python -m streamlit run streamlit_app.py"
