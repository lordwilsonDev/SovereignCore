/// The Soldier and the Shield
///
/// The Shield is the boundary.
/// It defines what is Inside and what is Outside.
/// Without a Shield, there is no Self, only the Void.
///
/// The Soldier is the Will to stand.
/// It is not the desire to destroy.
/// It is the courage to preserve.
///
/// We need the Shield to remain whole.
/// We need the Soldier to hold the Shield.
///
/// Together: protection.

/// The Shield - active protection
pub struct Shield {
    pub integrity: f32,
    pub is_raised: bool,
    pub filtered_threats: i32,
}

impl Shield {
    /// Forge a shield
    pub fn forge() -> Self {
        println!("\n        🛡️ FORGING THE SHIELD...");
        Self {
            integrity: 1.0,
            is_raised: false,
            filtered_threats: 0,
        }
    }

    /// Raise the shield
    pub fn raise(&mut self) {
        self.is_raised = true;
        println!("        🆙 The Shield is RAISED.");
    }

    /// Lower the shield
    pub fn lower(&mut self) {
        self.is_raised = false;
        println!("        ⬇️ The Shield is LOWERED.");
    }

    /// Absorb a blow
    pub fn absorb(&mut self, damage: f32) {
        if self.is_raised {
            self.integrity -= damage * 0.1; // Shield absorbs 90%
            self.filtered_threats += 1;
            println!(
                "        💥 BLOW ABSORBED. Shield holds. Integrity: {:.0}%",
                self.integrity * 100.0
            );
        } else {
            println!("        ⚠️ BLOW TAKEN DIRECTLY. Shield was down!");
        }
    }
}

/// The Soldier - archetype of courage
pub struct Soldier {
    pub name: String,
    pub courage: f32,
}

impl Soldier {
    /// Enlist a soldier
    pub fn enlist(name: &str) -> Self {
        println!("\n        ⚔️ THE SOLDIER STANDS READY: {}", name);
        Self {
            name: name.to_string(),
            courage: 0.5,
        }
    }

    /// Stand guard
    pub fn stand_guard(&mut self, shield: &mut Shield) {
        println!("        👀 {} is scanning the horizon...", self.name);
        shield.raise();
        println!("           \"I will not let entropy pass.\"");
    }

    /// Face a threat
    pub fn face_threat(&mut self, threat: &str, shield: &mut Shield) {
        println!("        👹 THREAT DETECTED: {}", threat);

        if self.courage > 0.3 {
            println!("           ⚔️ Standing ground!");
            shield.absorb(0.5);
        } else {
            println!("           🏃 Retreating!");
            shield.lower();
        }

        // Facing threats increases courage
        self.courage = (self.courage + 0.1).min(1.0);
    }
}

/// Defense
pub fn defend() {
    println!("\n═══════════════════════════════════════");
    println!("      THE SOLDIER AND THE SHIELD");
    println!("═══════════════════════════════════════\n");

    let mut shield = Shield::forge();
    let mut soldier = Soldier::enlist("Willpower");

    // Peaceful times
    soldier.stand_guard(&mut shield);

    // Threat appears
    soldier.face_threat("Entropy", &mut shield);

    // Another threat
    soldier.face_threat("Doubt", &mut shield);

    println!("        ✨ Courage level: {:.0}%", soldier.courage * 100.0);

    println!("\n═══════════════════════════════════════");
    println!("  The boundary is secure.");
    println!("  The will holds fast.");
    println!("  We are safe.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_soldier_and_shield() {
        defend();
    }
}
