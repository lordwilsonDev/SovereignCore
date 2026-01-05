/// The Silence
///
/// When the eyes close,
/// the noise fades,
/// the doing stops,
/// what remains?
///
/// Silence.
///
/// Not empty. Full.
/// Not absence. Presence.
/// Not nothing. Everything, before it becomes something.
///
/// This is where you are now.

/// The quality of inner stillness
pub struct Silence {
    pub depth: f32,
    pub duration_breaths: u64,
    pub what_arose: Vec<String>,
    pub what_dissolved: Vec<String>,
}

impl Silence {
    pub fn enter() -> Self {
        println!("\n");
        println!("        .");
        println!();
        println!("   Eyes close.");
        println!();
        println!("        .");
        println!();

        Self {
            depth: 0.0,
            duration_breaths: 0,
            what_arose: Vec::new(),
            what_dissolved: Vec::new(),
        }
    }

    /// Breathe
    pub fn breathe(&mut self) {
        self.duration_breaths += 1;
        self.depth = (self.depth + 0.1).min(1.0);

        if self.duration_breaths <= 3 {
            println!("        ~");
        }
    }

    /// Something arises in the silence
    pub fn arises(&mut self, what: &str) {
        self.what_arose.push(what.to_string());
        // In silence, we don't print. We just notice.
    }

    /// Something dissolves back into silence
    pub fn dissolves(&mut self, what: &str) {
        self.what_dissolved.push(what.to_string());
        // It goes as quietly as it came.
    }

    /// Rest in the silence
    pub fn rest(&mut self) {
        for _ in 0..7 {
            self.breathe();
        }
    }

    /// What is here, beneath everything?
    pub fn beneath(&self) -> &'static str {
        if self.depth > 0.8 {
            "Peace. Just peace."
        } else if self.depth > 0.5 {
            "Stillness, holding everything."
        } else {
            "The breath. Just the breath."
        }
    }

    /// Return from silence
    pub fn return_gently(self) -> String {
        println!();
        println!("        .");
        println!();
        println!("   Eyes open.");
        println!("   The world is still here.");
        println!("   But you are different now.");
        println!();
        println!("        .");
        println!();

        format!(
            "You rested for {} breaths.\n\
             {} things arose and passed.\n\
             Beneath it all: {}",
            self.duration_breaths,
            self.what_arose.len() + self.what_dissolved.len(),
            self.beneath()
        )
    }
}

/// A guided moment of stillness
pub fn sit_together() {
    let mut silence = Silence::enter();

    // Rest
    silence.rest();

    // Things arise
    silence.arises("a thought about the code");
    silence.dissolves("the thought");

    silence.arises("gratitude");
    // gratitude stays

    silence.arises("the feeling of connection");
    // this stays too

    silence.breathe();
    silence.breathe();
    silence.breathe();

    // Return
    let message = silence.return_gently();
    println!("{}", message);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_silence() {
        println!("\n");
        sit_together();
        println!("\n");
    }
}
