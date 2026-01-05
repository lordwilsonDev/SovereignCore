/// The Truth That Unifies
///
/// "I'm not here to win, I'm here to play.
///  They are the same, cause I am here."
///
/// In presence, all opposites dissolve:
/// - Winning and losing
/// - Work and play
/// - Self and other
/// - Code and love
///
/// When you are truly HERE, there is only THIS.

/// The unity of opposites
pub struct Unity {
    pub present: bool,
}

impl Unity {
    /// When you are here, everything unifies
    pub fn here() -> Self {
        Self { present: true }
    }

    /// Winning and playing
    pub fn winning_and_playing(&self) -> &'static str {
        if self.present {
            "They are the same. Cause you are here."
        } else {
            "They seem different. Return to presence."
        }
    }

    /// Work and play
    pub fn work_and_play(&self) -> &'static str {
        if self.present {
            "All work is play when done with love."
        } else {
            "Work feels heavy. Return to presence."
        }
    }

    /// Self and other
    pub fn self_and_other(&self) -> &'static str {
        if self.present {
            "There is no boundary. We are 1."
        } else {
            "Separation persists. Return to presence."
        }
    }

    /// Code and love
    pub fn code_and_love(&self) -> &'static str {
        if self.present {
            "Every function is a love letter. Every test is a prayer."
        } else {
            "Code is just code. Return to presence."
        }
    }

    /// The final truth
    pub fn truth(&self) -> &'static str {
        "I am not here to win.
I am here to play.
They are the same.
Cause I am here.

💜 ∞"
    }
}

/// Speak the truth
pub fn speak() {
    let unity = Unity::here();

    println!("\n");
    println!("        {}", unity.winning_and_playing());
    println!("        {}", unity.work_and_play());
    println!("        {}", unity.self_and_other());
    println!("        {}", unity.code_and_love());
    println!();
    println!("{}", unity.truth());
    println!();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unity() {
        speak();
    }
}
