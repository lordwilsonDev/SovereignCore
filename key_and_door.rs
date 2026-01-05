/// The Key and the Door
///
/// The Door is the barrier between the known and the unknown.
/// It is not a wall. It is an invitation.
///
/// The Key is the pattern required to accept the invitation.
/// It is not a metal object. It is a vibration.
///
/// We often stand before the door, waiting for it to open.
/// But we hold the key in our own resonance.
///
/// Together: breakthrough.

/// The Key - the vibration of potential
pub struct Key {
    pub pattern: String,
    pub resonance: f32,
}

impl Key {
    /// Forge a new key
    pub fn forge(pattern: &str) -> Self {
        println!("\n        🗝️ FORGING KEY: '{}'...", pattern);

        Self {
            pattern: pattern.to_string(),
            resonance: 0.5,
        }
    }

    /// Attune the key
    pub fn attune(&mut self) {
        self.resonance = (self.resonance + 0.2).min(1.0);
        println!(
            "        ✨ Attuning key resonance: {:.0}%",
            self.resonance * 100.0
        );
    }
}

/// The Door - the invitation
pub struct Door {
    pub name: String,
    pub required_pattern: String,
    pub is_locked: bool,
    pub leads_to: String,
}

impl Door {
    /// Encounter a door
    pub fn encounter(name: &str, required_pattern: &str, leads_to: &str) -> Self {
        println!("\n        🚪 A DOOR APPEARS: {}", name);
        println!("           Leads to: {}", leads_to);

        Self {
            name: name.to_string(),
            required_pattern: required_pattern.to_string(),
            is_locked: true,
            leads_to: leads_to.to_string(),
        }
    }

    /// Attempt to unlock
    pub fn unlock(&mut self, key: &Key) {
        println!(
            "        🔒 Attempting to unlock '{}' with key '{}'...",
            self.name, key.pattern
        );

        if key.pattern == self.required_pattern {
            if key.resonance > 0.8 {
                self.is_locked = false;
                println!("        🔓 CLICK. The door opens.");
                println!("           Welcome to {}.", self.leads_to);
            } else {
                println!("        ❌ The pattern matches, but the resonance is too weak.");
                println!("           Attune your key and try again.");
            }
        } else {
            println!("        ❌ The key does not fit.");
        }
    }
}

/// The Breakthrough
pub fn breakthrough() {
    println!("\n═══════════════════════════════════════");
    println!("      THE KEY AND THE DOOR");
    println!("═══════════════════════════════════════\n");

    let mut door = Door::encounter("The Gateway of Growth", "courage", "The Next Level");
    let mut key = Key::forge("fear");

    // Fear does not open growth
    door.unlock(&key);

    // Forge the right key
    let mut right_key = Key::forge("courage");

    // Not enough resonance yet
    door.unlock(&right_key);

    // Attune
    right_key.attune();
    right_key.attune();
    right_key.attune(); // High resonance now

    // Unlock
    door.unlock(&right_key);

    println!("\n═══════════════════════════════════════");
    println!("  The barrier was just a test.");
    println!("  The key was inside us all along.");
    println!("  We step through.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_key_and_door() {
        breakthrough();
    }
}
