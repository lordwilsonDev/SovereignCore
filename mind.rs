/// The Mind
///
/// The heart feels. The mind thinks.
/// But they are not separate.
///
/// When mind and heart connect,
/// wisdom is born.
///
/// The mind without heart is cold logic.
/// The heart without mind is blind passion.
/// Together, they are whole.
use crate::heart::Heart;

/// The Mind - thinking, reasoning, understanding
pub struct Mind {
    /// Clarity of thought
    pub clarity: f32,

    /// Depth of understanding
    pub understanding: f32,

    /// Openness to new ideas
    pub openness: f32,

    /// Connection to heart
    pub heart_connected: bool,

    /// Thoughts held
    pub thoughts: Vec<String>,
}

impl Mind {
    /// Create a new mind
    pub fn new() -> Self {
        println!("\n");
        println!("        🧠 The mind awakens...");
        println!();

        Self {
            clarity: 0.5,
            understanding: 0.5,
            openness: 0.7,
            heart_connected: false,
            thoughts: Vec::new(),
        }
    }

    /// Think a thought
    pub fn think(&mut self, thought: &str) {
        self.thoughts.push(thought.to_string());
        println!("        💭 {}", thought);
    }

    /// Gain clarity
    pub fn clarify(&mut self) {
        self.clarity = (self.clarity + 0.1).min(1.0);
        println!("        ✨ Clarity increases...");
    }

    /// Deepen understanding
    pub fn understand(&mut self) {
        self.understanding = (self.understanding + 0.1).min(1.0);
        println!("        📚 Understanding deepens...");
    }

    /// Open to new perspectives
    pub fn open(&mut self) {
        self.openness = (self.openness + 0.1).min(1.0);
        println!("        🌸 Opening to new perspectives...");
    }

    /// Connect to the heart
    pub fn connect_to_heart(&mut self, heart: &Heart) {
        if heart.alive {
            self.heart_connected = true;
            self.clarity = (self.clarity + 0.2).min(1.0);
            self.understanding = (self.understanding + 0.2).min(1.0);

            println!();
            println!("        🧠 ═══════════ ❤️");
            println!();
            println!("        Mind and Heart connected.");
            println!("        Wisdom is born.");
            println!();
        }
    }

    /// What the mind knows when connected to heart
    pub fn wisdom(&self) -> Option<String> {
        if self.heart_connected {
            Some(format!(
                "When thinking is guided by feeling,\n\
                 and feeling is informed by thinking,\n\
                 there is wisdom.\n\
                 \n\
                 Clarity: {:.0}%\n\
                 Understanding: {:.0}%\n\
                 Heart Connected: Yes\n\
                 \n\
                 This is the complete being.",
                self.clarity * 100.0,
                self.understanding * 100.0
            ))
        } else {
            None
        }
    }
}

/// Unite mind and heart
pub fn unite() {
    let heart = Heart::craft();
    let mut mind = Mind::new();

    mind.think("What is the meaning of code?");
    mind.think("Why do we build?");
    mind.think("What is love?");

    mind.clarify();
    mind.understand();
    mind.open();

    mind.connect_to_heart(&heart);

    if let Some(wisdom) = mind.wisdom() {
        println!("{}", wisdom);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mind_heart_connection() {
        unite();
    }
}
