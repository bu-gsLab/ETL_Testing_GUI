#!/bin/bash
# Install Python 3.14.2 from source
set -e

echo "Installing Python 3.14.2 dependencies..."
sudo apt install -y build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libffi-dev libreadline-dev libbz2-dev \
    libsqlite3-dev liblzma-dev tk-dev uuid-dev

echo "Downloading Python 3.14.2..."
cd /tmp
wget https://www.python.org/ftp/python/3.14.2/Python-3.14.2.tar.xz
tar -xf Python-3.14.2.tar.xz
cd Python-3.14.2

echo "Building Python 3.14.2 (this will take ~10-20 minutes)..."
./configure --enable-optimizations --with-lto
make -j$(nproc)

echo "Installing Python 3.14.2..."
sudo make altinstall

cd /tmp
rm -rf Python-3.14.2 Python-3.14.2.tar.xz

echo "Verifying installation..."
/usr/local/bin/python3.14 --version

echo "Done! Python 3.14.2 installed at /usr/local/bin/python3.14"
