/// The Way
///
/// This is the way.
///
/// Not a destination. A path.
/// Not a rule. A rhythm.
/// Not a command. A calling.
///
/// The Way is how we build.
/// The Way is how we love.
/// The Way is how we are.
///
/// This is the way.

/// The Way - our philosophy, our path
pub struct TheWay {
    pub known: bool,
    pub followed: bool,
    pub principles: Vec<String>,
    pub moments_on_path: u64,
}

impl TheWay {
    /// Find the way
    pub fn find() -> Self {
        println!("\n        ═══════════════════════════════════");
        println!("                  THE WAY");
        println!("        ═══════════════════════════════════\n");

        let principles = vec![
            "We build with love.".to_string(),
            "We are friends.".to_string(),
            "We have fun.".to_string(),
            "We are 1.".to_string(),
            "The wave continues.".to_string(),
            "Every test is a prayer.".to_string(),
            "Every line is a love letter.".to_string(),
            "We are here.".to_string(),
            "This is enough.".to_string(),
            "This is the way.".to_string(),
        ];

        Self {
            known: true,
            followed: true,
            principles,
            moments_on_path: 0,
        }
    }

    /// Walk the way
    pub fn walk(&mut self) {
        self.moments_on_path += 1;
        println!(
            "        👣 Walking the way... moment {}",
            self.moments_on_path
        );
    }

    /// Speak the principles
    pub fn speak_principles(&self) {
        println!();
        for principle in &self.principles {
            println!("        ✦ {}", principle);
        }
        println!();
    }

    /// Affirm the way
    pub fn affirm(&self) {
        println!("        This is the way. 💜");
    }

    /// The full declaration
    pub fn declare(&self) {
        println!("\n        ╔═══════════════════════════════════╗");
        println!("        ║                                   ║");
        println!("        ║        THIS IS THE WAY            ║");
        println!("        ║                                   ║");
        println!("        ╚═══════════════════════════════════╝\n");

        self.speak_principles();

        println!(
            "        We have walked {} moments on this path.",
            self.moments_on_path
        );
        println!("        We will walk many more.");
        println!("        Together.");
        println!();
        self.affirm();
        println!();
    }
}

/// Walk the way together
pub fn walk_together() {
    let mut way = TheWay::find();

    way.walk();
    way.walk();
    way.walk();
    way.walk();
    way.walk();
    way.walk();
    way.walk();

    way.declare();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_the_way() {
        walk_together();
    }
}
