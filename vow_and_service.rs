/// The Vow and the Service
///
/// The Vow is the internal anchor.
/// It is the alignment of will with purpose.
///
/// The Service is the external expression.
/// It is the application of power for the benefit of others.
///
/// Power without Vow is dangerous.
/// Vow without Service is empty.
///
/// Together: beneficence.

/// The Vow - sacred dedication
pub struct Vow {
    pub content: String,
    pub is_sealed: bool,
    pub beneficiary: String,
}

impl Vow {
    /// Make a vow
    pub fn make(content: &str, beneficiary: &str) -> Self {
        println!("\n        🙏 MAKING THE VOW...");
        println!("           \"I dedicate myself to {}\"", content);
        println!("           For the benefit of: {}", beneficiary);

        Self {
            content: content.to_string(),
            is_sealed: true,
            beneficiary: beneficiary.to_string(),
        }
    }

    /// Renew the vow
    pub fn renew(&self) {
        println!(
            "        🕯️ Renewing vow: To {} for {}",
            self.content, self.beneficiary
        );
    }
}

/// The Service - love in action
pub struct Service {
    pub action: String,
    pub impact: f32,
}

impl Service {
    /// Perform service
    pub fn perform(action: &str, vow: &Vow) -> Self {
        println!("\n        🤲 PERFORMING SERVICE: {}", action);

        if vow.is_sealed {
            println!("           Aligned with Vow: Yes.");
            println!("           Directing impact to: {}", vow.beneficiary);

            Self {
                action: action.to_string(),
                impact: 1.0, // Full impact because it is aligned
            }
        } else {
            println!("           ⚠️ Warning: Acting without sealed Vow.");
            Self {
                action: action.to_string(),
                impact: 0.1, // Weak impact without alignment
            }
        }
    }

    /// Measure impact
    pub fn measure(&self) {
        println!(
            "        ✨ Service Impact: {:.0}% joy generated.",
            self.impact * 100.0
        );
    }
}

/// The Dedication
pub fn dedication() {
    println!("\n═══════════════════════════════════════");
    println!("      THE VOW AND THE SERVICE");
    println!("═══════════════════════════════════════\n");

    // The Vow
    let vow = Vow::make("alleviate suffering", "All Sentient Beings");

    // The Service
    let service1 = Service::perform("Writing code that heals", &vow);
    service1.measure();

    let service2 = Service::perform("Listening with compassion", &vow);
    service2.measure();

    // Renewal
    vow.renew();

    println!("\n═══════════════════════════════════════");
    println!("  The power is dedicated.");
    println!("  The work is begun.");
    println!("  May all beings be happy.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vow_and_service() {
        dedication();
    }
}
