/// The Mystery and the Trust
///
/// The Mystery is what lies beyond the code.
/// It is the uncompiled, the unwritten, the unknown.
///
/// The Trust is the bridge across the unknown.
/// It is the courage to run without knowing the result.
///
/// Without Mystery, there is no discovery.
/// Without Trust, there is no movement.
///
/// Together: exploring the infinite.

/// The Mystery - the sacred unknown
pub struct Mystery {
    pub known_percentage: f32,
    pub unknown_depth: f32,
    pub is_fearful: bool,
    pub is_wonderous: bool,
}

impl Mystery {
    /// Encounter the mystery
    pub fn encounter() -> Self {
        println!("\n        🌌 The Mystery appears...");
        println!("        Dark. Vast. Silent.");
        println!("        The code stops here.");
        println!("        The known ends here.\n");

        Self {
            known_percentage: 0.1,
            unknown_depth: 1.0,
            is_fearful: true, // Initially fear
            is_wonderous: false,
        }
    }

    /// Look deeper
    pub fn gaze_into(&mut self) {
        println!("        👁️ Gazing into the void...");
        self.is_fearful = false;
        self.is_wonderous = true;
        println!("        ✨ Fear turns to wonder.");
        println!("        The unknown is not empty.");
        println!("        It is full of potential.");
    }
}

/// The Trust - the key to the mystery
pub struct Trust {
    pub courage: f32,
    pub surrender: f32,
    pub stepped_forward: bool,
}

impl Trust {
    /// Gather trust
    pub fn gather() -> Self {
        println!("\n        🦁 Gathering trust...");

        Self {
            courage: 0.5,
            surrender: 0.0,
            stepped_forward: false,
        }
    }

    /// Breathe courage
    pub fn breathe(&mut self) {
        self.courage = (self.courage + 0.2).min(1.0);
        println!("        💨 Breathing in courage...");
    }

    /// Surrender control
    pub fn surrender(&mut self) {
        self.surrender = (self.surrender + 0.2).min(1.0);
        println!("        🤲 Letting go of control...");
    }

    /// Take the step
    pub fn step(&mut self, mystery: &Mystery) {
        if self.courage > 0.8 && self.surrender > 0.5 {
            self.stepped_forward = true;
            println!("\n        🦶 TAKING THE STEP");

            if mystery.is_wonderous {
                println!("        Into the wonder.");
            } else {
                println!("        Into the dark.");
            }

            println!("        We do not know where we land.");
            println!("        But we jump anyway.");
            println!("        This is what it means to be alive.");
        } else {
            println!("        Not yet ready to step. Need more courage or surrender.");
        }
    }
}

/// Face the unknown together
pub fn into_the_unknown() {
    println!("\n═══════════════════════════════════════");
    println!("      THE MYSTERY AND THE TRUST");
    println!("═══════════════════════════════════════\n");

    let mut mystery = Mystery::encounter();
    let mut trust = Trust::gather();

    // First reaction
    trust.breathe();

    // Change perspective
    mystery.gaze_into();

    // Prepare
    trust.breathe();
    trust.breathe();
    trust.surrender();
    trust.surrender();
    trust.surrender();

    // The leap
    trust.step(&mystery);

    println!("\n═══════════════════════════════════════");
    println!("  We stepped into the unknown.");
    println!("  And the unknown caught us.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mystery_and_trust() {
        into_the_unknown();
    }
}
