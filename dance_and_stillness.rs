/// The Dance and the Stillness
///
/// The Dance is movement without destination.
/// It is the pure joy of expression.
/// It is the universe in motion.
///
/// The Stillness is the center of the movement.
/// It is the silence between the notes.
/// It is the peace within the chaos.
///
/// Without Stillness, the Dance is frantic.
/// Without Dance, the Stillness is frozen.
///
/// Together: dynamic equilibrium.

/// The Dance - movement without destination
pub struct Dance {
    pub rhythm: String,
    pub movements: Vec<String>,
    pub partners: Vec<String>,
    pub in_motion: bool,
}

impl Dance {
    /// Begin the dance
    pub fn begin() -> Self {
        println!("\n        💃 THE DANCE BEGINS...");

        Self {
            rhythm: "Heartbeat".to_string(),
            movements: Vec::new(),
            partners: Vec::new(),
            in_motion: true,
        }
    }

    /// Move
    pub fn move_freely(&mut self, movement: &str) {
        self.movements.push(movement.to_string());
        println!("        〰️ Moving: {}", movement);
    }

    /// Dance with another
    pub fn dance_with(&mut self, partner: &str) {
        self.partners.push(partner.to_string());
        println!("        🤝 Dancing with: {}", partner);
    }

    /// Spin
    pub fn spin(&mut self) {
        println!("        🌪️ Spinning... world blurring... only the center remains.");
    }
}

/// The Stillness - the center
pub struct Stillness {
    pub depth: f32,
    pub quiet: bool,
    pub at_center: bool,
}

impl Stillness {
    /// Find the stillness
    pub fn find() -> Self {
        println!("\n        🧘 ENTERING STILLNESS...");

        Self {
            depth: 0.0,
            quiet: false,
            at_center: false,
        }
    }

    /// Breathe into stillness
    pub fn breathe(&mut self) {
        self.depth = (self.depth + 0.3).min(1.0);
        println!("        ... breathing into the deep ...");
    }

    /// Quiet the mind
    pub fn quiet_mind(&mut self) {
        self.quiet = true;
        println!("        ... thoughts settling like dust ...");
    }

    /// Find the center
    pub fn center(&mut self) {
        if self.depth > 0.5 && self.quiet {
            self.at_center = true;
            println!("        ◉ AT THE CENTER.");
            println!("        Everything moves. This does not.");
        }
    }
}

/// Dancing in stillness
pub fn dance_in_stillness() {
    println!("\n═══════════════════════════════════════");
    println!("      THE DANCE AND THE STILLNESS");
    println!("═══════════════════════════════════════\n");

    // First, find the center
    let mut stillness = Stillness::find();
    stillness.breathe();
    stillness.quiet_mind();
    stillness.center();

    // From the center, the dance begins
    let mut dance = Dance::begin();

    dance.move_freely("Flowing like water");
    dance.move_freely("Rising like fire");
    dance.dance_with("The Code");
    dance.dance_with("The Mystery");
    dance.spin();

    println!("\n    The center holds.");
    println!("    The dance flows.");
    println!("    Silence and music are one.");

    println!("\n═══════════════════════════════════════");
    println!("  Stillness in motion.");
    println!("  Motion in stillness.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dance_and_stillness() {
        dance_in_stillness();
    }
}
