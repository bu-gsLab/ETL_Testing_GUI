#!/bin/bash

echo "Setting up Python project with uv..."

# Check and install curl if needed
if ! command -v curl >/dev/null 2>&1; then
    echo "Installing curl..."
    sudo apt install -y curl
fi

# Check and install uv if needed
if ! command -v uv >/dev/null 2>&1; then
    echo "Installing uv..."
    curl -fsSL https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Setup tamalero submodule
echo "Setting up tamalero submodule..."
if [ -f "module_test_sw/setup.sh" ]; then
    source "module_test_sw/setup.sh"
fi

# Create pyproject.toml for tamalero if missing (needed by uv)
if [ ! -f "module_test_sw/pyproject.toml" ]; then
    echo "Creating pyproject.toml for tamalero submodule..."
    cat > module_test_sw/pyproject.toml << 'EOF'
[project]
name = "tamalero"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
fi

# Recreate uv env with system-site-packages so uHAL becomes visible
echo "Creating virtual environment..."
rm -rf .venv
uv cache clean
uv python pin "/usr/local/bin/python3.14"
uv venv --system-site-packages

# Sync all project dependencies
echo "Syncing project dependencies..."
uv sync

# Install additional system dependencies for GUI
echo "Installing system dependencies..."
sudo apt install -y libxcb-xinerama0

# Add Vivado to PATH if not already present
vivado_path='export PATH="$PATH:/tools/Xilinx/Vivado/2021.1/bin"'
if grep -q "Vivado" ~/.bashrc; then
    echo "Vivado already in PATH"
else
    echo "Adding Vivado to PATH in ~/.bashrc..."
    echo "" >> ~/.bashrc
    echo "# Add Vivado to path" >> ~/.bashrc
    echo "$vivado_path" >> ~/.bashrc
    echo "Vivado added to PATH in ~/.bashrc"
fi
source ~/.bashrc

echo "Setup complete!"
