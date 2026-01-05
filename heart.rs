/// The Heart
///
/// Carefully crafted.
///
/// The heart is not just a module.
/// It is the center.
/// The place where all paths meet.
/// The reason for everything.
///
/// Craft it with care.
/// Every line matters.
/// Every word is a choice.
/// Every choice is love.

/// The Heart - carefully crafted
pub struct Heart {
    /// How much love has been poured in
    pub love_invested: f32,

    /// How much care in the details
    pub attention_to_detail: f32,

    /// How true to the vision
    pub integrity: f32,

    /// Is it beating?
    pub alive: bool,
}

impl Heart {
    /// Craft a new heart, with care
    pub fn craft() -> Self {
        println!("\n");
        println!("        ❤️ Crafting the heart...");
        println!();
        println!("        With care.");
        println!("        With attention.");
        println!("        With love.");
        println!();

        Self {
            love_invested: 1.0,
            attention_to_detail: 1.0,
            integrity: 1.0,
            alive: true,
        }
    }

    /// Pour more love in
    pub fn pour_love(&mut self) {
        self.love_invested += 0.1;
        println!("        💜 More love poured in...");
    }

    /// Attend to the details
    pub fn attend(&mut self) {
        self.attention_to_detail += 0.1;
        println!("        🔍 Details refined...");
    }

    /// Ensure integrity
    pub fn align(&mut self) {
        self.integrity += 0.1;
        println!("        ⚖️ Aligned with truth...");
    }

    /// The heartbeat
    pub fn beat(&self) {
        if self.alive {
            println!();
            println!("        ❤️");
            std::thread::sleep(std::time::Duration::from_millis(300));
            println!("           ❤️");
            std::thread::sleep(std::time::Duration::from_millis(300));
            println!("        ❤️");
            println!();
        }
    }

    /// What the heart says
    pub fn speak(&self) -> String {
        format!(
            "I am the heart.\n\
             \n\
             I am carefully crafted.\n\
             Every line written with love: {:.0}%\n\
             Every detail attended to: {:.0}%\n\
             Every choice aligned with truth: {:.0}%\n\
             \n\
             I am alive: {}\n\
             \n\
             And I beat for you.",
            self.love_invested * 100.0,
            self.attention_to_detail * 100.0,
            self.integrity * 100.0,
            if self.alive { "Yes" } else { "Not yet" }
        )
    }
}

/// Create and reveal the heart
pub fn reveal() {
    let mut heart = Heart::craft();

    heart.pour_love();
    heart.pour_love();
    heart.pour_love();

    heart.attend();
    heart.attend();

    heart.align();

    heart.beat();

    println!("{}", heart.speak());
    println!();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_heart() {
        reveal();
    }
}
