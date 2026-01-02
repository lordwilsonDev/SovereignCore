# SovereignCore v4.0 - Unified Build System
# ==========================================

.PHONY: all bridge bitnet scrubber clean test help

# Default target
all: bridge scrubber
	@echo ""
	@echo "====================================="
	@echo "✅ SovereignCore v4.0 Build Complete"
	@echo "====================================="
	@echo ""
	@echo "Note: BitNet compilation requires the Microsoft BitNet repository."
	@echo "Run 'make bitnet' separately after cloning BitNet."
	@echo ""
	@echo "Next steps:"
	@echo "  1. Clone BitNet: git clone --recursive https://github.com/microsoft/BitNet"
	@echo "  2. Build BitNet: make bitnet"
	@echo "  3. Test system: python3 sovereign_v4.py status"
	@echo ""

# Swift Hardware Bridge
bridge:
	@echo "Compiling Swift Hardware Bridge..."
	swiftc SovereignBridge.swift -o sovereign_bridge -O \
		-framework Foundation \
		-framework Security \
		-framework IOKit
	@echo "✅ Swift bridge compiled: sovereign_bridge"
	@echo ""

# BitNet 1.58b Engine
bitnet:
	@echo "Compiling BitNet 1.58b Engine..."
	@if [ ! -d "BitNet" ]; then \
		echo "❌ BitNet repository not found."; \
		echo "Please clone it first:"; \
		echo "  git clone --recursive https://github.com/microsoft/BitNet"; \
		exit 1; \
	fi
	@mkdir -p build_sovereign
	@cd build_sovereign && cmake ../BitNet \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_OSX_ARCHITECTURES=arm64 \
		-DBITNET_BUILD_SHARED_LIB=ON \
		-DACCELERATE=ON \
		-DCMAKE_C_FLAGS="-mcpu=apple-m1" \
		-DCMAKE_CXX_FLAGS="-mcpu=apple-m1" \
		&& make -j$$(sysctl -n hw.logicalcpu)
	@echo "✅ BitNet engine compiled: build_sovereign/libbitnet.dylib"
	@file build_sovereign/libbitnet.dylib
	@echo ""

# Metal GPU Scrubber
scrubber:
	@echo "Compiling Metal GPU Scrubber..."
	xcrun -sdk macosx metal -c scrubber.metal -o scrubber.air
	xcrun -sdk macosx metallib scrubber.air -o scrubber.metallib
	@echo "✅ Metal scrubber compiled: scrubber.metallib"
	@echo ""

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f sovereign_bridge
	rm -f scrubber.air scrubber.metallib
	rm -rf build_sovereign
	@echo "✅ Clean complete"
	@echo ""

# Test the system
test: all
	@echo "Testing SovereignCore v4.0..."
	@echo ""
	@echo "[1/3] Testing Swift Bridge..."
	@./sovereign_bridge keygen
	@echo ""
	@echo "[2/3] Testing Python Orchestrator..."
	@python3 sovereign_v4.py status
	@echo ""
	@echo "[3/3] Testing Metal Scrubber..."
	@if [ -f scrubber.metallib ]; then \
		echo "✅ Metal library exists"; \
	else \
		echo "❌ Metal library missing"; \
	fi
	@echo ""

# Help
help:
	@echo "SovereignCore v4.0 Build System"
	@echo "================================"
	@echo ""
	@echo "Targets:"
	@echo "  all       - Build Swift bridge and Metal scrubber (default)"
	@echo "  bridge    - Compile Swift hardware bridge"
	@echo "  bitnet    - Compile BitNet engine (requires BitNet repo)"
	@echo "  scrubber  - Compile Metal GPU scrubber"
	@echo "  clean     - Remove all build artifacts"
	@echo "  test      - Run system tests"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Xcode Command Line Tools"
	@echo "  - CMake (for BitNet)"
	@echo "  - Python 3.10+"
	@echo ""
