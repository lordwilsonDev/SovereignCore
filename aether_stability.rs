/// Aether Stability Monitor
///
/// Implements the "Bug Hunters" from the Aether Blueprint:
/// 1. Lyapunov Exponent Monitor - Detects "Vanishing Chaos"
/// 2. Conservation Assertion - Detects "Reversibility Leak"
/// 3. Phase-Locked Loop - Prevents "Phantom Photon" sync drift
use std::time::Instant;

/// Monitors the Lyapunov exponent to ensure the reservoir stays in chaotic regime
pub struct LyapunovMonitor {
    pub trajectory_a: Vec<f32>,
    pub trajectory_b: Vec<f32>,
    pub separation_history: Vec<f32>,
    pub chaos_threshold: f32,
}

impl LyapunovMonitor {
    pub fn new(chaos_threshold: f32) -> Self {
        Self {
            trajectory_a: Vec::new(),
            trajectory_b: Vec::new(),
            separation_history: Vec::new(),
            chaos_threshold,
        }
    }

    /// Record two initially close state vectors
    pub fn record_trajectories(&mut self, state_a: Vec<f32>, state_b: Vec<f32>) {
        self.trajectory_a = state_a;
        self.trajectory_b = state_b;

        // Calculate separation distance
        let separation: f32 = self
            .trajectory_a
            .iter()
            .zip(self.trajectory_b.iter())
            .map(|(a, b)| (a - b).powi(2))
            .sum::<f32>()
            .sqrt();

        self.separation_history.push(separation);
    }

    /// Calculate Lyapunov exponent: rate of exponential separation
    pub fn calculate_exponent(&self) -> f32 {
        if self.separation_history.len() < 2 {
            return 0.0;
        }

        let n = self.separation_history.len();
        let d0 = self.separation_history[0].max(1e-10);
        let dn = self.separation_history[n - 1].max(1e-10);

        // λ = (1/t) * ln(d(t)/d(0))
        (dn / d0).ln() / (n as f32)
    }

    /// Check if system is still chaotic (λ > 0)
    pub fn is_chaotic(&self) -> bool {
        self.calculate_exponent() > self.chaos_threshold
    }

    /// Returns perturbation if chaos is vanishing
    pub fn get_noise_perturbation(&self) -> Option<f32> {
        if !self.is_chaotic() {
            // Inject noise to kick back into chaos
            Some(
                0.01 * (std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos()
                    % 1000) as f32
                    / 1000.0,
            )
        } else {
            None
        }
    }
}

/// Validates reversibility of computations
pub struct ConservationAssertion {
    pub input_cache: Vec<f32>,
    pub tolerance: f32,
}

impl ConservationAssertion {
    pub fn new(tolerance: f32) -> Self {
        Self {
            input_cache: Vec::new(),
            tolerance,
        }
    }

    /// Cache input before forward pass
    pub fn cache_input(&mut self, input: &[f32]) {
        self.input_cache = input.to_vec();
    }

    /// Verify: Input == Inverse(Forward(Input))
    pub fn verify_reversibility(&self, recovered: &[f32]) -> Result<(), String> {
        if self.input_cache.len() != recovered.len() {
            return Err("Conservation Violation: Size mismatch".to_string());
        }

        let error: f32 = self
            .input_cache
            .iter()
            .zip(recovered.iter())
            .map(|(a, b)| (a - b).abs())
            .sum::<f32>()
            / self.input_cache.len() as f32;

        if error > self.tolerance {
            return Err(format!(
                "Reversibility Leak Detected: Error {} exceeds tolerance {}",
                error, self.tolerance
            ));
        }

        println!(
            "✅ Conservation Assertion PASSED: Reversibility error = {:.6}",
            error
        );
        Ok(())
    }
}

/// Software Phase-Locked Loop for delay synchronization
pub struct PhaseLock {
    pub target_period_ns: u64,
    pub last_injection: Instant,
    pub phase_error_history: Vec<i64>,
    pub adjustment_gain: f64,
}

impl PhaseLock {
    pub fn new(target_period_ns: u64) -> Self {
        Self {
            target_period_ns,
            last_injection: Instant::now(),
            phase_error_history: Vec::new(),
            adjustment_gain: 0.1,
        }
    }

    /// Mark injection time and calculate phase error
    pub fn mark_injection(&mut self) -> i64 {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last_injection).as_nanos() as i64;
        let phase_error = elapsed - self.target_period_ns as i64;

        self.phase_error_history.push(phase_error);
        self.last_injection = now;

        phase_error
    }

    /// Get adjusted delay to compensate for drift
    pub fn get_adjusted_delay(&self) -> u64 {
        if self.phase_error_history.is_empty() {
            return self.target_period_ns;
        }

        let avg_error: f64 = self
            .phase_error_history
            .iter()
            .rev()
            .take(10)
            .map(|&e| e as f64)
            .sum::<f64>()
            / 10.0;

        let adjustment = (avg_error * self.adjustment_gain) as i64;
        (self.target_period_ns as i64 - adjustment).max(1000) as u64
    }

    /// Check if system is in sync
    pub fn is_locked(&self) -> bool {
        if self.phase_error_history.len() < 5 {
            return false;
        }

        let recent_errors: Vec<i64> = self
            .phase_error_history
            .iter()
            .rev()
            .take(5)
            .copied()
            .collect();

        let variance: f64 = {
            let mean = recent_errors.iter().sum::<i64>() as f64 / recent_errors.len() as f64;
            recent_errors
                .iter()
                .map(|&e| (e as f64 - mean).powi(2))
                .sum::<f64>()
                / recent_errors.len() as f64
        };

        variance < (self.target_period_ns as f64 * 0.1).powi(2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lyapunov_monitor() {
        let mut monitor = LyapunovMonitor::new(-0.1);

        // Simulate diverging trajectories (chaotic)
        for i in 0..10 {
            let scale = 1.0 + i as f32 * 0.1;
            let state_a: Vec<f32> = (0..10).map(|j| j as f32 * 0.1).collect();
            let state_b: Vec<f32> = (0..10).map(|j| j as f32 * 0.1 * scale).collect();
            monitor.record_trajectories(state_a, state_b);
        }

        let exponent = monitor.calculate_exponent();
        println!("🔬 Lyapunov Exponent: {}", exponent);
        assert!(exponent > 0.0, "System should be chaotic");
    }

    #[test]
    fn test_conservation_assertion() {
        let mut assertion = ConservationAssertion::new(0.001);

        let input = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        assertion.cache_input(&input);

        // Perfect recovery
        let recovered = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        assert!(assertion.verify_reversibility(&recovered).is_ok());

        // Slight error within tolerance
        let recovered_noisy = vec![1.0001, 2.0001, 3.0001, 4.0001, 5.0001];
        assert!(assertion.verify_reversibility(&recovered_noisy).is_ok());
    }

    #[test]
    fn test_phase_lock() {
        let mut pll = PhaseLock::new(1_000_000); // 1ms target

        for _ in 0..10 {
            pll.mark_injection();
            std::thread::sleep(std::time::Duration::from_micros(1000));
        }

        let adjusted = pll.get_adjusted_delay();
        println!("🔒 PLL Adjusted Delay: {} ns", adjusted);
    }
}
