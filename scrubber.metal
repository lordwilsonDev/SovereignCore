#include <metal_stdlib>
using namespace metal;

// MARK: - Memory Scrubber Kernel
// Zeroes out buffer to sanitize residual thought vectors

kernel void scrub_memory(device float *buffer [[buffer(0)]],
                         uint id [[thread_position_in_grid]]) {
    buffer[id] = 0.0;
}

// MARK: - Thermodynamic Generator Kernel
// High-intensity math to generate thermal pressure for "Proof of Heat"

kernel void generate_entropy(device float *buffer [[buffer(0)]],
                             constant float &seed [[buffer(1)]],
                             uint id [[thread_position_in_grid]]) {
    float value = buffer[id];
    float s = seed;
    
    // Execute complex trigonometric operations to engage ALUs
    // This generates measurable heat on the GPU
    for (int i = 0; i < 500; i++) {
        value = fract(sin(dot(float2(value, s), float2(12.9898, 78.233))) * 43758.5453);
        s += 0.001;
    }
    
    buffer[id] = value;
}

// MARK: - Combined Scrub and Generate
// Scrubs memory then generates entropy in one pass

kernel void scrub_and_generate(device float *buffer [[buffer(0)]],
                               constant float &seed [[buffer(1)]],
                               uint id [[thread_position_in_grid]]) {
    // First scrub
    buffer[id] = 0.0;
    
    // Then generate
    float value = 0.0;
    float s = seed + float(id) * 0.0001;
    
    for (int i = 0; i < 500; i++) {
        value = fract(sin(dot(float2(value, s), float2(12.9898, 78.233))) * 43758.5453);
        s += 0.001;
    }
    
    buffer[id] = value;
}
