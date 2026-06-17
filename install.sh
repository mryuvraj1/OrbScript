cat > install.sh << 'ENDOFFILE'
#!/bin/bash
# (Paste the installer script from earlier)
ENDOFFILE

echo "Installing OrbScript..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.7 or later."
    if [ -d "/data/data/com.termux" ]; then
        echo "Termux detected. Install with: pkg install python"
    else
        echo "Install with your package manager (apt, yum, brew, etc.)"
    fi
    exit 1
fi

# Determine installation directory
if [ -d "/data/data/com.termux" ]; then
    INSTALL_DIR="$PREFIX/bin"
    echo "Termux detected. Installing to $INSTALL_DIR"
else
    INSTALL_DIR="/usr/local/bin"
    echo "Installing to $INSTALL_DIR"
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Copy all Python files
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp "$SCRIPT_DIR"/*.py .

# Create the orbscript executable
cat > orbscript << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add the installation directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == '__main__':
    main()
EOF

# Make executable
chmod +x orbscript
cp orbscript "$INSTALL_DIR/"
cp *.py "$INSTALL_DIR/"

# Create examples directory
EXAMPLES_DIR="$HOME/.orbscript/examples"
mkdir -p "$EXAMPLES_DIR"

# Cleanup
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo
echo "OrbScript installed successfully!"
echo "You can now use the 'orbscript' command from anywhere."
echo
echo "Try: orbscript run -c 'say \"Hello World\"'"
echo