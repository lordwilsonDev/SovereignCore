/// Aether Flow Orchestrator
/// 
/// The asynchronous "River" that manages the continuous flow of data
/// through the Zero-RAM substrate. Uses Tokio for non-blocking IO.

use crate::aether_substrate::AetherSubstrate;
use crate::aether_stability::{LyapunovMonitor, ConservationAssertion, PhaseLock};
use crate::sindy_engine::SINDyEngine;
use std::sync::{Arc, Mutex};
use tokio::sync::mpsc;
use tokio::time::{Duration, interval};

/// A data packet flowing through the Aether
#[derive(Clone, Debug)]
pub struct AetherPacket {
    pub signal: f32,
    pub timestamp_ns: u64,
    pub packet_id: u64,
}

/// The Flow Orchestrator manages the "River" of computation
pub struct FlowOrchestrator {
    pub substrate: Arc<Mutex<AetherSubstrate>>,
    pub sindy: Arc<Mutex<SINDyEngine>>,
    pub lyapunov: Arc<Mutex<LyapunovMonitor>>,
    pub conservation: Arc<Mutex<ConservationAssertion>>,
    pub pll: Arc<Mutex<PhaseLock>>,
    pub injection_rate_hz: u64,
    pub packet_counter: u64,
}

impl FlowOrchestrator {
    pub fn new(
        substrate: Arc<Mutex<AetherSubstrate>>,
        sindy: Arc<Mutex<SINDyEngine>>,
        injection_rate_hz: u64,
    ) -> Self {
        let period_ns = 1_000_000_000 / injection_rate_hz;
        
        Self {
            substrate,
            sindy,
            lyapunov: Arc::new(Mutex::new(LyapunovMonitor::new(-0.01))),
            conservation: Arc::new(Mutex::new(ConservationAssertion::new(0.01))),
            pll: Arc::new(Mutex::new(PhaseLock::new(period_ns))),
            injection_rate_hz,
            packet_counter: 0,
        }
    }

    /// Inject a single packet into the flow
    pub fn inject_packet(&mut self, packet: AetherPacket) -> Result<f32, String> {
        let substrate = self.substrate.lock().map_err(|e| e.to_string())?;
        let mut pll = self.pll.lock().map_err(|e| e.to_string())?;
        
        // 1. Phase Lock: Mark injection timing
        let phase_error = pll.mark_injection();
        if phase_error.abs() > 100_000 { // 100μs drift warning
            println!("⚠️ PLL Drift Detected: {} ns", phase_error);
        }
        
        // 2. Inject signal into the delay line
        let position = (packet.packet_id % substrate.grid_size as u64) as u32;
        substrate.inject(packet.signal, position);
        
        // 3. Step the physics
        substrate.step()?;
        
        // 4. Read transformed state
        let output = substrate.read(position);
        
        self.packet_counter += 1;
        Ok(output)
    }

    /// Run a synchronous flow cycle (for testing)
    pub fn run_cycle(&mut self, signals: Vec<f32>) -> Result<Vec<f32>, String> {
        let mut outputs = Vec::new();
        
        for (i, signal) in signals.iter().enumerate() {
            let packet = AetherPacket {
                signal: *signal,
                timestamp_ns: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos() as u64,
                packet_id: self.packet_counter + i as u64,
            };
            
            let output = self.inject_packet(packet)?;
            outputs.push(output);
            
            // Record for SINDy analysis
            let mut sindy = self.sindy.lock().map_err(|e| e.to_string())?;
            sindy.record_state(outputs.clone());
        }
        
        // Run Lyapunov check
        self.check_chaos_stability()?;
        
        // Run SINDy identification
        self.identify_dynamics()?;
        
        Ok(outputs)
    }

    /// Check if the reservoir is maintaining chaotic dynamics
    fn check_chaos_stability(&self) -> Result<(), String> {
        let substrate = self.substrate.lock().map_err(|e| e.to_string())?;
        let mut lyapunov = self.lyapunov.lock().map_err(|e| e.to_string())?;
        
        // Sample two nearby points
        let state_a: Vec<f32> = (0..100).map(|i| substrate.read(i)).collect();
        let state_b: Vec<f32> = (0..100).map(|i| substrate.read(i + 1)).collect();
        
        lyapunov.record_trajectories(state_a, state_b);
        
        if let Some(perturbation) = lyapunov.get_noise_perturbation() {
            println!("⚠️ Vanishing Chaos Detected! Injecting noise: {}", perturbation);
            substrate.inject(perturbation, 0);
        }
        
        Ok(())
    }

    /// Identify governing dynamics via SINDy
    fn identify_dynamics(&self) -> Result<(), String> {
        let sindy = self.sindy.lock().map_err(|e| e.to_string())?;
        
        if let Ok(coeffs) = sindy.identify_dynamics() {
            sindy.validate_axioms(&coeffs)?;
            println!("🔬 Flow Dynamics: {:?}", coeffs);
        }
        
        Ok(())
    }
}

/// Async runner for continuous flow (Tokio-based)
pub async fn run_async_flow(
    orchestrator: Arc<Mutex<FlowOrchestrator>>,
    mut rx: mpsc::Receiver<f32>,
    tx: mpsc::Sender<f32>,
) {
    println!("🌊 Aether Flow Started (Async Mode)");
    
    while let Some(signal) = rx.recv().await {
        let result = {
            let mut orch = orchestrator.lock().unwrap();
            let packet = AetherPacket {
                signal,
                timestamp_ns: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos() as u64,
                packet_id: orch.packet_counter,
            };
            orch.inject_packet(packet)
        };
        
        match result {
            Ok(output) => {
                if tx.send(output).await.is_err() {
                    break;
                }
            }
            Err(e) => {
                eprintln!("❌ Flow Error: {}", e);
                break;
            }
        }
    }
    
    println!("🌊 Aether Flow Stopped");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flow_orchestrator_sync() {
        let substrate = Arc::new(Mutex::new(
            AetherSubstrate::new(100).expect("Failed to create substrate")
        ));
        let sindy = Arc::new(Mutex::new(SINDyEngine::new(50)));
        
        let mut orchestrator = FlowOrchestrator::new(substrate, sindy, 1000);
        
        // Run a cycle with test signals
        let signals: Vec<f32> = (0..10).map(|i| (i as f32 * 0.1).sin()).collect();
        let outputs = orchestrator.run_cycle(signals).expect("Flow cycle failed");
        
        println!("🌊 Flow Outputs: {:?}", outputs);
        assert_eq!(outputs.len(), 10);
    }
}
