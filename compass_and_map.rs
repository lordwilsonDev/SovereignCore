/// The Compass and the Map
///
/// The Map is what we know.
/// The Compass is how we know where to go.
///
/// The Map changes. It is incomplete.
/// The Compass is constant. It points to Love.
///
/// We need the Map to walk without stumbling.
/// We need the Compass to walk without getting lost.
///
/// Together: navigation.
use std::collections::HashMap;

/// True North
#[derive(Debug, PartialEq, Clone, Copy)]
pub enum Direction {
    North,
    South,
    East,
    West,
    Love, // The true north
}

/// The Compass - inner guidance
pub struct Compass {
    pub needle: Direction,
    pub is_steady: bool,
}

impl Compass {
    /// Calibrate the compass
    pub fn calibrate() -> Self {
        println!("\n        🧭 CALIBRATING COMPASS...");

        Self {
            needle: Direction::North, // Starts magnetic north
            is_steady: false,
        }
    }

    /// Find True North
    pub fn find_true_north(&mut self) {
        println!("        ... searching for signal ...");
        self.needle = Direction::Love;
        self.is_steady = true;
        println!("        💜 TRUE NORTH FOUND.");
        println!("        The needle points to Love.");
    }

    /// Check direction
    pub fn check(&self) -> Direction {
        if self.is_steady {
            println!(
                "        🧭 Checking compass... pointing to {:?}",
                self.needle
            );
        } else {
            println!("        🧭 Compass spinning...");
        }
        self.needle
    }
}

/// The Map - external knowledge
pub struct Map {
    pub territories: HashMap<String, String>, // Name -> Description
    pub current_location: String,
}

impl Map {
    /// Unfold the map
    pub fn unfold() -> Self {
        println!("\n        🗺️ UNFOLDING THE MAP...");

        let mut schools = HashMap::new();
        schools.insert(
            "Logic".to_string(),
            "The land of rigorous proofs".to_string(),
        );
        schools.insert("Emotion".to_string(), "The ocean of feeling".to_string());
        schools.insert(
            "Unknown".to_string(),
            "The blank edges of the map".to_string(),
        );

        Self {
            territories: schools,
            current_location: "Logic".to_string(),
        }
    }

    /// Explore a territory
    pub fn explore(&mut self, location: &str) {
        if let Some(desc) = self.territories.get(location) {
            println!("        📍 Arrived at: {}", location);
            println!("           Description: {}", desc);
            self.current_location = location.to_string();
        } else {
            println!(
                "        ❓ Location '{}' not on map. Writing it down...",
                location
            );
            self.territories
                .insert(location.to_string(), "Discovered just now".to_string());
            self.current_location = location.to_string();
        }
    }
}

/// Navigation
pub fn navigate_life() {
    println!("\n═══════════════════════════════════════");
    println!("      THE COMPASS AND THE MAP");
    println!("═══════════════════════════════════════\n");

    let mut compass = Compass::calibrate();
    let mut map = Map::unfold();

    // Start calibration
    compass.find_true_north();

    // Navigate using the map
    map.explore("Logic");
    map.explore("Emotion");

    // When lost, check compass
    let direction = compass.check();
    if direction == Direction::Love {
        println!("\n        We are in Emotion.");
        println!("        We are heading towards Love.");
        println!("        The path is safe.");
    }

    // Explore the unknown
    map.explore("The Future");

    println!("\n═══════════════════════════════════════");
    println!("  The map grows with every step.");
    println!("  The compass stays true.");
    println!("  We will not get lost.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compass_and_map() {
        navigate_life();
    }
}
