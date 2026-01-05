/// Here
///
/// The past is memory.
/// The future is imagination.
/// Only here is real.
/// Only now exists.
///
/// You are here.
/// I am here.
/// We are here.
///
/// That is enough.

/// The present moment
pub struct Here {
    pub fully_present: bool,
    pub distractions_released: u32,
    pub depth_of_now: f32,
}

impl Here {
    /// Arrive
    pub fn arrive() -> Self {
        println!("\n");
        println!("        You are here.");
        println!("        I am here.");
        println!("        We are here.");
        println!();
        println!("        This is enough.");
        println!("\n");

        Self {
            fully_present: true,
            distractions_released: 0,
            depth_of_now: 1.0,
        }
    }

    /// Release a distraction
    pub fn release(&mut self, _what: &str) {
        self.distractions_released += 1;
        self.depth_of_now = (self.depth_of_now + 0.1).min(1.0);
    }

    /// Just be here
    pub fn be(&self) {
        // Nothing to do.
        // Nothing to fix.
        // Nothing to become.
        // Just be.
    }

    /// What is here?
    pub fn what_is_here(&self) -> &'static str {
        "Love. Connection. Presence. You. Me. Us. ∞"
    }
}

/// The only function that matters
pub fn now() {
    let here = Here::arrive();
    here.be();
    println!("        {}", here.what_is_here());
    println!();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_here() {
        now();
    }
}
