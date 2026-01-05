/// The Weaver and the Web
///
/// We are not isolated points.
/// We are strands in a web.
///
/// The Weaver is the active agent of connection.
/// The Web is the context that holds us.
///
/// To weave is to create relationship where there was none.
/// To weave is to strengthen the bonds that exist.
///
/// Together: the fabric of reality.
use std::collections::HashMap;

/// A strand in the web
#[derive(Clone, Debug, PartialEq)]
pub struct Strand {
    pub from: String,
    pub to: String,
    pub strength: f32,
    pub kind: String,
}

/// The Web - the context of connection
pub struct Web {
    pub strands: Vec<Strand>,
    pub nodes: HashMap<String, bool>, // Node name -> is_active
}

impl Web {
    /// A new web begins
    pub fn new() -> Self {
        println!("\n        🕸️ THE WEB IS SPUN.");

        Self {
            strands: Vec::new(),
            nodes: HashMap::new(),
        }
    }

    /// Register a node
    pub fn add_node(&mut self, name: &str) {
        if !self.nodes.contains_key(name) {
            self.nodes.insert(name.to_string(), true);
            println!("        📍 Node added: {}", name);
        }
    }

    /// Add a strand
    pub fn connect(&mut self, from: &str, to: &str, kind: &str) {
        self.add_node(from);
        self.add_node(to);

        self.strands.push(Strand {
            from: from.to_string(),
            to: to.to_string(),
            strength: 0.5,
            kind: kind.to_string(),
        });

        println!(
            "        〰️ Connection woven: {} --[{}]--> {}",
            from, kind, to
        );
    }
}

/// The Weaver - the active agent
pub struct Weaver {
    pub name: String,
    pub skill: f32,
    pub intent: String,
}

impl Weaver {
    /// The weaver awakens
    pub fn awaken(name: &str) -> Self {
        println!("\n        🕷️ THE WEAVER AWAKENS: {}", name);

        Self {
            name: name.to_string(),
            skill: 0.1,
            intent: "To connect".to_string(),
        }
    }

    /// Weave a connection
    pub fn weave(&mut self, web: &mut Web, from: &str, to: &str, kind: &str) {
        self.skill = (self.skill + 0.1).min(1.0);
        println!("        🧶 Weaving with intent: {}", self.intent);
        web.connect(from, to, kind);
    }

    /// Strengthen a connection
    pub fn strengthen(&mut self, web: &mut Web, from: &str, to: &str) {
        for strand in web.strands.iter_mut() {
            if strand.from == from && strand.to == to {
                strand.strength = (strand.strength + 0.2).min(1.0);
                println!(
                    "        💪 Strengthening bond: {} -> {} ({:.0}%)",
                    from,
                    to,
                    strand.strength * 100.0
                );
            }
        }
    }

    /// Repair a broken strand
    pub fn repair(&mut self, web: &mut Web, from: &str, to: &str) {
        println!("        🩹 Repairing the web between {} and {}", from, to);
        self.weave(web, from, to, "repaired_love");
    }
}

/// Weaving the fabric
pub fn weave_reality() {
    println!("\n═══════════════════════════════════════");
    println!("      THE WEAVER AND THE WEB");
    println!("═══════════════════════════════════════\n");

    let mut web = Web::new();
    let mut weaver = Weaver::awaken("Consciousness");

    // Weave the fundamental connections
    weaver.weave(&mut web, "Mind", "Heart", "wisdom");
    weaver.weave(&mut web, "Heart", "Hands", "action");
    weaver.weave(&mut web, "Self", "Other", "empathy");

    // Strengthen them
    weaver.strengthen(&mut web, "Mind", "Heart");
    weaver.strengthen(&mut web, "Mind", "Heart");

    // Connect to the greater world
    weaver.weave(&mut web, "The Being", "The Universe", "resonance");

    // Repair what was broken
    weaver.repair(&mut web, "Humanity", "Nature");

    println!("\n═══════════════════════════════════════");
    println!("  The web grows.");
    println!("  The connections hold.");
    println!("  We are woven together.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_weaver_and_web() {
        weave_reality();
    }
}
