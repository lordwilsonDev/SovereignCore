#!/bin/bash
# Standard installation script

echo "Installing SovereignCore v5.0 dependencies..."
cargo build --release
# pip install -r requirements.txt
echo "Classical wrapper layer installed successfully."
