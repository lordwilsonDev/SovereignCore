use metal::*;

pub struct AetherSubstrate {
    pub device: Device,
    pub command_queue: CommandQueue,
    pub pipeline: ComputePipelineState,
    pub buffer: Buffer,
    pub grid_size: u32,
    pub delay_tau: u32,
}

impl AetherSubstrate {
    pub fn new(delay_tau: u32) -> Result<Self, String> {
        let device = Device::system_default().ok_or("No Metal device found")?;
        let command_queue = device.new_command_queue();

        // Internal Grid Size: 1M Virtual Nodes (4MB in float32)
        let grid_size = 1048576;
        let buffer_size = (grid_size * 4) as u64;

        // Allocate buffer in Shared/Unified Memory
        let buffer = device.new_buffer(buffer_size, MTLResourceOptions::StorageModeShared);

        // Load and Compile the Shader
        // Note: In production, we'd use a precompiled .metallib
        // For our "Aether" prototype, we load raw source if possible or use default library
        let source = include_str!("aether_reservoir.metal");
        let options = CompileOptions::new();
        let library = device
            .new_library_with_source(source, &options)
            .map_err(|e| format!("Shader compilation failed: {}", e))?;

        let kernel = library
            .get_function("mackey_glass_kernel", None)
            .map_err(|e| format!("Kernel function not found: {}", e))?;

        let pipeline = device
            .new_compute_pipeline_state_with_function(&kernel)
            .map_err(|e| format!("Pipeline state creation failed: {}", e))?;

        Ok(Self {
            device,
            command_queue,
            pipeline,
            buffer,
            grid_size,
            delay_tau,
        })
    }

    /// Inject a signal into the delay line loop (Zero-Copy)
    pub fn inject(&self, value: f32, position: u32) {
        let ptr = self.buffer.contents() as *mut f32;
        let p = (position % self.grid_size) as usize;
        unsafe {
            *ptr.add(p) = value;
        }
    }

    /// Read a state from the delay line
    pub fn read(&self, position: u32) -> f32 {
        let ptr = self.buffer.contents() as *const f32;
        let p = (position % self.grid_size) as usize;
        unsafe { *ptr.add(p) }
    }

    /// Dispatch the Mackey-Glass physics update
    pub fn step(&self) -> Result<(), String> {
        let command_buffer = self.command_queue.new_command_buffer();
        let encoder = command_buffer.new_compute_command_encoder();

        encoder.set_compute_pipeline_state(&self.pipeline);
        encoder.set_buffer(0, Some(&self.buffer), 0);

        // Pass constants (tau, a, b)
        let a = 0.2f32;
        let b = 0.1f32;
        encoder.set_bytes(1, 4, &self.delay_tau as *const u32 as *const _);
        encoder.set_bytes(2, 4, &a as *const f32 as *const _);
        encoder.set_bytes(3, 4, &b as *const f32 as *const _);

        let threads_per_group = MTLSize::new(256, 1, 1);
        let grid_size = MTLSize::new(self.grid_size as u64, 1, 1);

        encoder.dispatch_threads(grid_size, threads_per_group);
        encoder.end_encoding();

        command_buffer.commit();
        command_buffer.wait_until_completed();

        Ok(())
    }
}
