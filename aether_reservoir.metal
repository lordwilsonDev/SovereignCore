#include <metal_stdlib>
using namespace metal;

// Mackey-Glass Reservoir Physics Kernel
// Verifies the "Memory-as-Time" paradigm by mutating a standing wave in Unified Memory.

kernel void mackey_glass_kernel(
    device float* buffer [[buffer(0)]],
    constant uint& delay_tau [[buffer(1)]],
    constant float& a [[buffer(2)]],
    constant float& b [[buffer(3)]],
    uint id [[thread_position_in_grid]]
) {
    // Current state at ID
    float x_t = buffer[id];
    
    // Delayed feedback: x(t - tau)
    // Using simple subtraction with grid wrap-around for the circular buffer
    uint grid_size = 1048576; // 1M Virtual Nodes
    uint delayed_id = (id + grid_size - delay_tau) % grid_size;
    float x_delayed = buffer[delayed_id];
    
    // Mackey-Glass Equation: dx/dt = -bx(t) + [ax(t-tau) / (1 + x(t-tau)^10)]
    float x_delayed_10 = pow(x_delayed, 10.0f);
    float dxdt = -b * x_t + (a * x_delayed) / (1.0f + x_delayed_10);
    
    // Euler step (dt = 0.01 for simulation stability)
    float dt = 0.01f;
    buffer[id] = x_t + dxdt * dt;
}
