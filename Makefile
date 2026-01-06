# SovereignCore v4.0 Makefile
# Unified build system for all components

.PHONY: all bridge scrubber clean run help

# Paths
BRIDGE_SRC = SovereignBridge.swift
BRIDGE_BIN = sovereign_bridge
METAL_SRC = scrubber.metal
METAL_AIR = scrubber.air
METAL_LIB = scrubber.metallib

# Compiler flags
SWIFT_FLAGS = -O -framework Foundation -framework Security -framework IOKit
METAL_SDK = macosx

# Default target
all: bridge scrubber
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           SovereignCore v4.0 Build Complete                  ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Run: python3 sovereign_v4.py"
	@echo ""

# Swift Hardware Bridge
bridge: $(BRIDGE_SRC)
	@echo ">> Compiling Swift Hardware Bridge..."
	swiftc $(BRIDGE_SRC) -o $(BRIDGE_BIN) $(SWIFT_FLAGS)
	@chmod +x $(BRIDGE_BIN)
	@echo "✓ Bridge compiled: $(BRIDGE_BIN)"

# Metal GPU Scrubber
scrubber: $(METAL_SRC)
	@echo ">> Compiling Metal Kernels..."
	xcrun -sdk $(METAL_SDK) metal -c $(METAL_SRC) -o $(METAL_AIR)
	xcrun -sdk $(METAL_SDK) metallib $(METAL_AIR) -o $(METAL_LIB)
	@rm -f $(METAL_AIR)
	@echo "✓ Metal library: $(METAL_LIB)"

# Run SovereignCore
run: all
	@python3 sovereign_v4.py

# Show status
status:
	@python3 sovereign_v4.py --status

# List models
models:
	@python3 sovereign_v4.py --list-models

# Clean build artifacts
clean:
	@echo ">> Cleaning build artifacts..."
	rm -f $(BRIDGE_BIN)
	rm -f $(METAL_AIR) $(METAL_LIB)
	@echo "✓ Clean complete"

# Help
help:
	@echo "SovereignCore v4.0 Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make all      - Build all components"
	@echo "  make bridge   - Compile Swift hardware bridge"
	@echo "  make scrubber - Compile Metal GPU kernels"
	@echo "  make run      - Build and run SovereignCore"
	@echo "  make status   - Show system status"
	@echo "  make models   - List available Ollama models"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make help     - Show this help"
