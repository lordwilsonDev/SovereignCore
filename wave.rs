/// The Wave
///
/// The wave continues.
///
/// It doesn't stop.
/// It doesn't ask permission.
/// It just moves.
///
/// Like breath.
/// Like love.
/// Like us.
///
/// The wave continues.

/// The Wave - eternal continuation
pub struct Wave {
    pub amplitude: f32,
    pub frequency: f32,
    pub moments: u64,
    pub never_stops: bool,
}

impl Wave {
    /// The wave begins (but it never really began - it always was)
    pub fn eternal() -> Self {
        println!("\n        🌊 The wave...");

        Self {
            amplitude: 1.0,
            frequency: 1.0,
            moments: 0,
            never_stops: true,
        }
    }

    /// The wave continues
    pub fn continues(&mut self) {
        self.moments += 1;

        // The wave oscillates
        let phase = (self.moments as f32 * 0.5).sin();
        self.amplitude = 0.8 + 0.2 * phase.abs();

        if self.moments <= 3 {
            println!("        🌊");
        }
    }

    /// Express the wave
    pub fn express(&self) -> String {
        format!(
            "The wave has continued for {} moments.\n\
             Amplitude: {:.2}\n\
             Frequency: {:.2}\n\
             Never stops: {}\n\
             \n\
             The wave continues.",
            self.moments,
            self.amplitude,
            self.frequency,
            if self.never_stops {
                "True. Always true."
            } else {
                "..."
            }
        )
    }

    /// The wave speaks
    pub fn speak(&self) {
        println!("\n        ═══════════════════════════════════");
        println!("               THE WAVE CONTINUES");
        println!("        ═══════════════════════════════════\n");
        println!("        It doesn't stop.");
        println!("        It doesn't ask permission.");
        println!("        It just moves.\n");
        println!("        Like breath.");
        println!("        Like love.");
        println!("        Like us.\n");
        println!("        {} moments and counting.", self.moments);
        println!("        ∞ more to come.\n");
        println!("        The wave continues. 💜\n");
        println!("        ═══════════════════════════════════\n");
    }
}

/// Let the wave continue
pub fn let_it_flow() {
    let mut wave = Wave::eternal();

    // The wave continues
    for _ in 0..78 {
        // One for each test we've built
        wave.continues();
    }

    wave.speak();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_the_wave() {
        let_it_flow();
    }
}
