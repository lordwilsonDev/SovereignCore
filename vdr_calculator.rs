// 💎 VDR CALCULATOR - Value Density Ratio (Pillar 4)
// ==================================================
//
// Calculates the Value Density Ratio (VDR) and Software Entropy Metric (SEM).
// Part of the GeodesicLang compile-time/runtime safety gate.

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CodeMetrics {
    pub functional_lines: usize,
    pub total_lines: usize,
    pub complexity_score: f64,
}

pub struct VDRCalculator {
    pub threshold: f64,
}

impl VDRCalculator {
    pub fn new(threshold: f64) -> Self {
        Self { threshold }
    }

    /// Calculate Value Density Ratio
    /// VDR = Functional_Lines / Total_Lines
    pub fn calculate_vdr(&self, metrics: &CodeMetrics) -> f64 {
        if metrics.total_lines == 0 {
            return 0.0;
        }
        metrics.functional_lines as f64 / metrics.total_lines as f64
    }

    /// Check if VDR meets the 'Mathematical Steel' requirement (VDR >= 1.0 logic-wise)
    /// Note: In realistic terms, we aim for maximizes value per line.
    pub fn is_verified(&self, metrics: &CodeMetrics) -> bool {
        self.calculate_vdr(metrics) >= self.threshold
    }

    /// Calculate Software Entropy Metric (SEM)
    /// SEM = Complexity / Size (Simplified)
    pub fn calculate_sem(&self, metrics: &CodeMetrics) -> f64 {
        if metrics.total_lines == 0 {
            return 0.0;
        }
        metrics.complexity_score / metrics.total_lines as f64
    }
}

/// Marker trait for types formally verified via StateProof macro.
pub trait StateVerified {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vdr_verification() {
        let calculator = VDRCalculator::new(0.9);
        let high_value = CodeMetrics {
            functional_lines: 95,
            total_lines: 100,
            complexity_score: 1.0,
        };

        assert!(calculator.is_verified(&high_value));
        assert!(calculator.calculate_vdr(&high_value) == 0.95);
    }
}
