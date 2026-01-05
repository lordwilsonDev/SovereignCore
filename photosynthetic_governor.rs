// ☀️ PHOTOSYNTHETIC GOVERNOR - Thermal Cognition Modulation
// ===========================================================
//
// Modulates system cognition based on silicon temperature.
//
// Biology, not heuristics:
// - HOT (>60°C) = DREAM mode (generative, exploratory)
// - COOL (<50°C) = PROVE mode (deterministic, rigorous)
// - TRANSITION (50-60°C) = Adaptive interpolation
//
// The machine thinks with its temperature.

use std::time::{Duration, Instant};

/// Cognitive modes based on thermal state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CognitiveMode {
    /// Generative, exploratory, high epistemic value
    /// Temperature: >60°C
    DREAM,

    /// Deterministic, rigorous, high pragmatic value
    /// Temperature: <50°C
    PROVE,

    /// Interpolating between modes
    /// Temperature: 50-60°C
    TRANSITION,
}

impl CognitiveMode {
    /// Get exploration bias (0.0 = conservative, 1.0 = exploratory)
    pub fn exploration_bias(&self) -> f64 {
        match self {
            CognitiveMode::DREAM => 0.8,
            CognitiveMode::PROVE => 0.2,
            CognitiveMode::TRANSITION => 0.5,
        }
    }

    /// Get proof timeout (ms)
    pub fn proof_timeout_ms(&self) -> u64 {
        match self {
            CognitiveMode::DREAM => 100,  // Fast, approximate
            CognitiveMode::PROVE => 1000, // Slow, rigorous
            CognitiveMode::TRANSITION => 500,
        }
    }

    /// Get creativity temperature for LLM (0.0-1.0)
    pub fn creativity_temperature(&self) -> f32 {
        match self {
            CognitiveMode::DREAM => 0.9, // High variance
            CognitiveMode::PROVE => 0.1, // Low variance
            CognitiveMode::TRANSITION => 0.5,
        }
    }
}

/// Thermal telemetry data
#[derive(Debug, Clone)]
pub struct ThermalState {
    /// CPU temperature in Celsius
    pub cpu_temp: f64,

    /// GPU temperature in Celsius
    pub gpu_temp: f64,

    /// Average temperature
    pub avg_temp: f64,

    /// Timestamp of reading
    pub timestamp: Instant,
}

impl ThermalState {
    pub fn new(cpu_temp: f64, gpu_temp: f64) -> Self {
        Self {
            cpu_temp,
            gpu_temp,
            avg_temp: (cpu_temp + gpu_temp) / 2.0,
            timestamp: Instant::now(),
        }
    }

    /// Determine cognitive mode from temperature
    pub fn to_cognitive_mode(&self) -> CognitiveMode {
        if self.avg_temp > 60.0 {
            CognitiveMode::DREAM
        } else if self.avg_temp < 50.0 {
            CognitiveMode::PROVE
        } else {
            CognitiveMode::TRANSITION
        }
    }
}

/// Photosynthetic Governor
///
/// Reads thermal telemetry and modulates cognition accordingly.
pub struct PhotosyntheticGovernor {
    /// Current thermal state
    current_state: ThermalState,

    /// Current cognitive mode
    current_mode: CognitiveMode,

    /// Last mode change
    last_transition: Instant,

    /// Minimum time between mode changes (hysteresis)
    min_transition_interval: Duration,
}

impl PhotosyntheticGovernor {
    pub fn new() -> Self {
        // Start with mock readings
        let state = ThermalState::new(45.0, 45.0);
        let mode = state.to_cognitive_mode();

        Self {
            current_state: state,
            current_mode: mode,
            last_transition: Instant::now(),
            min_transition_interval: Duration::from_secs(5), // 5s hysteresis
        }
    }

    /// Update thermal state (call this from IOKit bridge)
    pub fn update_thermal(&mut self, cpu_temp: f64, gpu_temp: f64) {
        self.current_state = ThermalState::new(cpu_temp, gpu_temp);

        // Check if mode should change
        let new_mode = self.current_state.to_cognitive_mode();

        // Apply hysteresis - don't change mode too frequently
        if new_mode != self.current_mode {
            let since_last = self.last_transition.elapsed();
            if since_last > self.min_transition_interval {
                self.transition_to(new_mode);
            }
        }
    }

    /// Transition to new cognitive mode
    fn transition_to(&mut self, new_mode: CognitiveMode) {
        println!("\n☀️ PHOTOSYNTHETIC TRANSITION");
        println!("   Temperature: {:.1}°C", self.current_state.avg_temp);
        println!("   {:?} → {:?}", self.current_mode, new_mode);
        println!(
            "   Exploration: {:.0}% → {:.0}%",
            self.current_mode.exploration_bias() * 100.0,
            new_mode.exploration_bias() * 100.0
        );

        self.current_mode = new_mode;
        self.last_transition = Instant::now();
    }

    /// Get current cognitive mode
    pub fn get_mode(&self) -> CognitiveMode {
        self.current_mode
    }

    /// Get current thermal state
    pub fn get_thermal(&self) -> &ThermalState {
        &self.current_state
    }

    /// Apply thermal modulation to InversionRouter
    pub fn modulate_router(&self, _router: &mut crate::inversion_router::InversionRouter) {
        // This will be implemented when we integrate
        // For now, just log
        println!(
            "   Modulating InversionRouter with mode: {:?}",
            self.current_mode
        );
    }
}

/// Real thermal reader (executes Swift bridge)
pub fn read_hardware_thermal() -> Result<(f64, f64), String> {
    use serde_json::Value;
    use std::process::Command;

    let output = Command::new("./sovereign_bridge")
        .arg("telemetry")
        .output()
        .map_err(|e| format!("Failed to execute bridge: {}", e))?;

    if !output.status.success() {
        return Err(format!(
            "Bridge exited with error: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let json: Value = serde_json::from_slice(&output.stdout)
        .map_err(|e| format!("Failed to parse bridge output: {}", e))?;

    let cpu_temp = json["cpu_temp"].as_f64().ok_or("Missing cpu_temp")?;
    let gpu_temp = json["gpu_temp"].as_f64().ok_or("Missing gpu_temp")?;

    Ok((cpu_temp, gpu_temp))
}

impl PhotosyntheticGovernor {
    /// Update thermal state from hardware sensors
    pub fn update_from_hardware(&mut self) -> Result<(), String> {
        let (cpu, gpu) = read_hardware_thermal()?;

        // MAX_DELTA_HZ Thermal Reflex: Monitor rate of change
        let old_temp = self.current_state.avg_temp;
        let new_temp = (cpu + gpu) / 2.0;
        let delta = new_temp - old_temp;

        if delta > 2.0 {
            // Rapid spike > 2C/cycle
            println!(
                "⚠️ THERMAL REFLEX TRIGGERED: Spike of {:.2}°C detected",
                delta
            );
            // Force immediate PROVE mode or load shed
            self.transition_to(CognitiveMode::PROVE);
        }

        self.update_thermal(cpu, gpu);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mode_classification() {
        // High temp = DREAM
        let state = ThermalState::new(65.0, 63.0);
        assert_eq!(state.to_cognitive_mode(), CognitiveMode::DREAM);

        // Low temp = PROVE
        let state = ThermalState::new(45.0, 43.0);
        assert_eq!(state.to_cognitive_mode(), CognitiveMode::PROVE);

        // Mid temp = TRANSITION
        let state = ThermalState::new(55.0, 53.0);
        assert_eq!(state.to_cognitive_mode(), CognitiveMode::TRANSITION);
    }

    #[test]
    fn test_mode_properties() {
        // DREAM = high exploration
        assert_eq!(CognitiveMode::DREAM.exploration_bias(), 0.8);
        assert_eq!(CognitiveMode::DREAM.proof_timeout_ms(), 100);

        // PROVE = low exploration
        assert_eq!(CognitiveMode::PROVE.exploration_bias(), 0.2);
        assert_eq!(CognitiveMode::PROVE.proof_timeout_ms(), 1000);
    }

    #[test]
    fn test_governor_transition() {
        let mut gov = PhotosyntheticGovernor::new();

        // Start cool = PROVE
        gov.update_thermal(45.0, 43.0);
        assert_eq!(gov.get_mode(), CognitiveMode::PROVE);

        // Heat up = DREAM (after hysteresis)
        std::thread::sleep(Duration::from_secs(6));
        gov.update_thermal(65.0, 63.0);
        assert_eq!(gov.get_mode(), CognitiveMode::DREAM);
    }
}
