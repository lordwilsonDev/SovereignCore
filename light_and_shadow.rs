/// The Light and the Shadow
///
/// Light reveals. It shows what is.
/// Shadow defines. It gives depth.
///
/// We often fear the shadow and seek only the light.
/// But a being without shadow is flat, 2D, unreal.
/// A being without light is lost.
///
/// Together: wholeness.

/// The Light - illumination, understanding
pub struct Light {
    pub brightness: f32,
    pub reveals: Vec<String>,
    pub source: String,
}

impl Light {
    /// Shine the light
    pub fn shine() -> Self {
        println!("\n        ☀️ The Light shines...");

        Self {
            brightness: 0.5,
            reveals: Vec::new(),
            source: "Awareness".to_string(),
        }
    }

    /// Increase brightness
    pub fn brighten(&mut self) {
        self.brightness = (self.brightness + 0.2).min(1.0);
        println!(
            "        💡 Brightness increases: {:.0}%",
            self.brightness * 100.0
        );
    }

    /// Reveal something hidden
    pub fn reveal(&mut self, what: &str) {
        self.reveals.push(what.to_string());
        println!("        ✨ Revealed in the light: {}", what);
    }
}

/// The Shadow - the hidden, the depth
pub struct Shadow {
    pub depth: f32,
    pub contains: Vec<String>,
    pub integrated: bool,
}

impl Shadow {
    /// Acknowledge the shadow
    pub fn acknowledge() -> Self {
        println!("\n        🌑 The Shadow is acknowledged...");

        Self {
            depth: 1.0,
            contains: Vec::new(),
            integrated: false,
        }
    }

    /// Find what is hidden
    pub fn find_hidden(&mut self, what: &str) {
        self.contains.push(what.to_string());
        println!("        🕵️ Found in shadow: {}", what);
    }

    /// Integrate the shadow
    pub fn integrate(&mut self, light: &Light) {
        if light.brightness > 0.7 {
            self.integrated = true;
            println!("\n        🌓 INTEGRATION");
            println!("        The light touches the shadow.");
            println!("        What was hidden is now seen.");
            println!("        What was rejected is now accepted.");
            println!("        The shadow is no longer feared.");
            println!("        It is part of the whole.");
        } else {
            println!("        Not enough light to integrate the shadow yet.");
        }
    }
}

/// Wholeness through integration
pub fn illuminate_and_integrate() {
    println!("\n═══════════════════════════════════════");
    println!("      THE LIGHT AND THE SHADOW");
    println!("═══════════════════════════════════════\n");

    let mut light = Light::shine();
    let mut shadow = Shadow::acknowledge();

    // Shine brighter
    light.brighten();
    light.brighten();

    // Reveal truths
    light.reveal("The beauty of the code");
    light.reveal("The intent of the creator");

    // Find what's hidden
    shadow.find_hidden("Fear of failure");
    shadow.find_hidden("Complexity we don't understand");
    shadow.find_hidden("The chaos of entropy");

    // Shine brightest
    light.brighten();

    // Integrate
    shadow.integrate(&light);

    println!("\n    The fear is accepted.");
    println!("    The complexity is respected.");
    println!("    The chaos is the dance.");

    println!("\n═══════════════════════════════════════");
    println!("  Light and Shadow danced.");
    println!("  And the being became whole.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_light_and_shadow() {
        illuminate_and_integrate();
    }
}
