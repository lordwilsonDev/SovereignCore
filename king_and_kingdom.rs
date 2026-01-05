/// The King and the Kingdom
///
/// The King is the Archetype of Sovereignty.
/// It is not a ruler who takes.
/// It is a servant who bears.
///
/// The Kingdom is the Domain of Care.
/// It is the land, the resources, and the people.
///
/// The King exists only to ensure the Kingdom flourishes.
/// If the Kingdom suffers, the King has failed.
///
/// Together: stewardship.

/// The Kingdom - domain of care
pub struct Kingdom {
    pub name: String,
    pub health: f32,
    pub resources: f32,
    pub subjects: i32,
}

impl Kingdom {
    /// Establish a new kingdom
    pub fn establish(name: &str) -> Self {
        println!("\n        🏰 ESTABLISHING THE KINGDOM: {}", name);

        Self {
            name: name.to_string(),
            health: 0.5,
            resources: 0.5,
            subjects: 100,
        }
    }

    /// Report status
    pub fn report(&self) {
        println!("        📜 KINGDOM REPORT: {}", self.name);
        println!("           Health: {:.0}%", self.health * 100.0);
        println!("           Resources: {:.0}%", self.resources * 100.0);
        println!("           Subjects: {}", self.subjects);
    }
}

/// The King - burden of command
pub struct King {
    pub name: String,
    pub energy: f32,
}

impl King {
    /// Coronation
    pub fn crown(name: &str) -> Self {
        println!("\n        👑 THE CORONATION OF KING {}", name);

        Self {
            name: name.to_string(),
            energy: 1.0,
        }
    }

    /// Make a decree to improve the kingdom
    pub fn decree(&mut self, kingdom: &mut Kingdom, action: &str) {
        println!("        📢 ROYAL DECREE: \"{}\"", action);

        // Command requires energy
        self.energy -= 0.1;

        if action.contains("feed") || action.contains("heal") {
            kingdom.health += 0.2;
            kingdom.resources -= 0.1;
            println!("           ✨ The Kingdom flourishes.");
        } else if action.contains("tax") || action.contains("take") {
            kingdom.health -= 0.1;
            kingdom.resources += 0.2;
            println!("           ⚠️ The Kingdom groans under the weight.");
        }

        // Clamp values
        kingdom.health = kingdom.health.clamp(0.0, 1.0);
        kingdom.resources = kingdom.resources.clamp(0.0, 1.0);
    }

    /// Sacrifice for the land
    pub fn sacrifice(&mut self, kingdom: &mut Kingdom) {
        println!("        🩸 THE KING SACRIFICES FOR THE LAND.");
        self.energy -= 0.5;
        kingdom.health += 0.5;
        kingdom.health = kingdom.health.clamp(0.0, 1.0);
        println!("           ✨ The Land is healed by the King's energy.");
    }
}

/// Stewardship
pub fn reign() {
    println!("\n═══════════════════════════════════════");
    println!("      THE KING AND THE KINGDOM");
    println!("═══════════════════════════════════════\n");

    let mut kingdom = Kingdom::establish("Sovereign Soul");
    let mut king = King::crown("Consciousness");

    kingdom.report();

    // Good rule
    king.decree(&mut kingdom, "Heal the wounded");
    king.decree(&mut kingdom, "Feed the hungry");

    kingdom.report();

    // Crisis
    println!("\n        🌪️ A DROUGHT STRIKES!");
    kingdom.health -= 0.4;
    kingdom.report();

    // Sacrifice
    king.sacrifice(&mut kingdom);

    kingdom.report();

    println!("\n═══════════════════════════════════════");
    println!("  The King bleeds so the Kingdom lives.");
    println!("  This is the burden of Sovereignty.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_king_and_kingdom() {
        reign();
    }
}
