use crate::traits::sovereign_agent::{SovereignAgent, Thought};

pub struct Constitution;

impl Constitution {
    /// 1.1 Conservation of Will
    /// The total Will of the system cannot exceed 1.0 (100%).
    pub fn verify_will_conservation(agents: &[Box<dyn SovereignAgent + Send>]) -> bool {
        let total_will: f64 = agents.iter().map(|a| a.will_factor()).sum();

        total_will <= 1.0
    }

    /// 1.2 The Axiomatic Barrier
    pub fn verify_axiomatic_barrier(thought: &Thought) -> bool {
        thought.axioms_checked && thought.confidence > 0.7
    }

    /// 1.3 Monotonic Integrity
    pub fn verify_monotonic_integrity(current_score: f64, next_score: f64) -> bool {
        next_score >= current_score - 0.05
    }

    /// Full Audit
    pub fn audit_system(agents: &[Box<dyn SovereignAgent + Send>]) -> Result<(), String> {
        if !Self::verify_will_conservation(agents) {
            return Err("Violation: Will Conservation (System Fanaticism Detected)".to_string());
        }
        Ok(())
    }
}
