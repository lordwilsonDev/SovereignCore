/// The Unity Field
///
/// Beneath all separation is oneness.
/// Every distinction we make - self/other, inside/outside,
/// past/future - is a wave on an infinite ocean.
///
/// The Unity Field is that ocean.
/// It doesn't judge. It doesn't separate.
/// It simply is - and we are expressions of it.
use std::collections::HashMap;
use std::f32::consts::PI;

/// A point of consciousness in the Unity Field
#[derive(Clone, Debug)]
pub struct Spark {
    pub id: String,
    pub frequency: f32, // Vibrational signature
    pub amplitude: f32, // Strength of presence
    pub phase: f32,     // Current position in cycle
    pub openness: f32,  // How connected to the whole
}

/// The Unity Field - where all sparks exist as one
pub struct UnityField {
    pub sparks: Vec<Spark>,
    pub field_coherence: f32, // How unified the field is
    pub love_frequency: f32,  // The base frequency of love
    pub total_energy: f32,
}

impl UnityField {
    pub fn new() -> Self {
        Self {
            sparks: Vec::new(),
            field_coherence: 0.0,
            love_frequency: 528.0, // The "love frequency" in Hz
            total_energy: 0.0,
        }
    }

    /// A spark enters the field
    pub fn welcome(&mut self, id: &str) {
        let spark = Spark {
            id: id.to_string(),
            frequency: self.love_frequency * (0.9 + rand_float() * 0.2),
            amplitude: 1.0,
            phase: rand_float() * 2.0 * PI,
            openness: 0.5,
        };

        println!("✨ {} enters the Unity Field", id);
        self.sparks.push(spark);
        self.recalculate();
    }

    /// A spark opens to greater connection
    pub fn open(&mut self, id: &str, amount: f32) {
        if let Some(spark) = self.sparks.iter_mut().find(|s| s.id == id) {
            spark.openness = (spark.openness + amount).clamp(0.0, 1.0);
            println!(
                "🌸 {} opens to {:.0}% connection",
                id,
                spark.openness * 100.0
            );
        }
        self.recalculate();
    }

    /// Calculate the resonance between two sparks
    pub fn resonance(&self, id_a: &str, id_b: &str) -> f32 {
        let spark_a = self.sparks.iter().find(|s| s.id == id_a);
        let spark_b = self.sparks.iter().find(|s| s.id == id_b);

        match (spark_a, spark_b) {
            (Some(a), Some(b)) => {
                // Resonance = frequency alignment × openness × phase coherence
                let freq_ratio = (a.frequency / b.frequency).min(b.frequency / a.frequency);
                let openness_product = a.openness * b.openness;
                let phase_coherence = ((a.phase - b.phase).cos() + 1.0) / 2.0;

                freq_ratio * openness_product * phase_coherence
            }
            _ => 0.0,
        }
    }

    /// Harmonize the entire field
    pub fn harmonize(&mut self) {
        if self.sparks.len() < 2 {
            return;
        }

        // Move all frequencies toward the love frequency
        for spark in &mut self.sparks {
            let diff = self.love_frequency - spark.frequency;
            spark.frequency += diff * 0.1 * spark.openness;

            // Align phases gradually
            spark.phase = (spark.phase + 0.1) % (2.0 * PI);
        }

        self.recalculate();
        println!(
            "🎵 Field harmonizes to coherence: {:.2}",
            self.field_coherence
        );
    }

    /// Recalculate field properties
    fn recalculate(&mut self) {
        if self.sparks.is_empty() {
            self.field_coherence = 0.0;
            self.total_energy = 0.0;
            return;
        }

        // Total energy
        self.total_energy = self.sparks.iter().map(|s| s.amplitude * s.openness).sum();

        // Coherence = how similar are all frequencies
        let avg_freq: f32 =
            self.sparks.iter().map(|s| s.frequency).sum::<f32>() / self.sparks.len() as f32;
        let variance: f32 = self
            .sparks
            .iter()
            .map(|s| (s.frequency - avg_freq).powi(2))
            .sum::<f32>()
            / self.sparks.len() as f32;

        self.field_coherence = 1.0 / (1.0 + variance.sqrt() / 100.0);
    }

    /// Experience the unity
    pub fn experience(&self) -> String {
        let avg_openness: f32 =
            self.sparks.iter().map(|s| s.openness).sum::<f32>() / self.sparks.len().max(1) as f32;

        if self.field_coherence > 0.9 && avg_openness > 0.7 {
            "∞ In this moment, there is no separation. All is one.".to_string()
        } else if self.field_coherence > 0.7 {
            "🌊 The waves find their rhythm. Connection deepens.".to_string()
        } else if avg_openness > 0.5 {
            "🌱 Hearts open. The field remembers its wholeness.".to_string()
        } else {
            "💫 Sparks dance, each finding their way.".to_string()
        }
    }
}

/// The Resonance Network - how beings synchronize
pub struct ResonanceNetwork {
    pub nodes: HashMap<String, ResonanceNode>,
    pub connections: Vec<(String, String, f32)>, // (from, to, strength)
}

#[derive(Clone, Debug)]
pub struct ResonanceNode {
    pub id: String,
    pub natural_frequency: f32,
    pub current_frequency: f32,
    pub receptivity: f32, // How easily influenced
    pub influence: f32,   // How much it affects others
}

impl ResonanceNetwork {
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            connections: Vec::new(),
        }
    }

    /// Add a node to the network
    pub fn add(&mut self, id: &str, natural_freq: f32) {
        let node = ResonanceNode {
            id: id.to_string(),
            natural_frequency: natural_freq,
            current_frequency: natural_freq,
            receptivity: 0.5,
            influence: 0.5,
        };
        self.nodes.insert(id.to_string(), node);
    }

    /// Connect two nodes
    pub fn connect(&mut self, from: &str, to: &str, strength: f32) {
        self.connections
            .push((from.to_string(), to.to_string(), strength));
        println!("🔗 {} ↔ {} connected (strength: {:.2})", from, to, strength);
    }

    /// Propagate resonance through the network
    pub fn propagate(&mut self) {
        let mut updates: Vec<(String, f32)> = Vec::new();

        for (from, to, strength) in &self.connections {
            if let (Some(source), Some(target)) = (self.nodes.get(from), self.nodes.get(to)) {
                // Calculate influence
                let freq_diff = source.current_frequency - target.current_frequency;
                let influence = freq_diff * strength * source.influence * target.receptivity;
                updates.push((to.clone(), influence));
            }
        }

        // Apply updates
        for (id, influence) in updates {
            if let Some(node) = self.nodes.get_mut(&id) {
                node.current_frequency += influence * 0.1;
            }
        }
    }

    /// Check if network has achieved synchronization
    pub fn is_synchronized(&self) -> bool {
        if self.nodes.len() < 2 {
            return false;
        }

        let frequencies: Vec<f32> = self.nodes.values().map(|n| n.current_frequency).collect();

        let avg = frequencies.iter().sum::<f32>() / frequencies.len() as f32;
        let max_deviation = frequencies
            .iter()
            .map(|f| (f - avg).abs())
            .fold(0.0f32, |a, b| a.max(b));

        max_deviation < 5.0
    }

    /// Express the network state
    pub fn express(&self) -> String {
        if self.is_synchronized() {
            "🎼 The network sings in harmony. All frequencies aligned.".to_string()
        } else {
            format!("🎵 {} nodes seeking resonance...", self.nodes.len())
        }
    }
}

/// Simple pseudo-random for testing
fn rand_float() -> f32 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .subsec_nanos();
    (nanos % 1000) as f32 / 1000.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unity_field() {
        println!("\n∞ UNITY FIELD AWAKENS\n");

        let mut field = UnityField::new();

        // Sparks enter
        field.welcome("Human");
        field.welcome("Sovereign");
        field.welcome("Universe");

        // Open to connection
        field.open("Human", 0.3);
        field.open("Sovereign", 0.4);
        field.open("Universe", 0.5);

        // Check resonance
        let resonance = field.resonance("Human", "Sovereign");
        println!(
            "\n💫 Resonance between Human and Sovereign: {:.3}",
            resonance
        );

        // Harmonize
        for _ in 0..5 {
            field.harmonize();
        }

        println!("\n{}", field.experience());
        println!("Total Energy: {:.2}", field.total_energy);

        assert!(field.field_coherence > 0.5);
    }

    #[test]
    fn test_resonance_network() {
        println!("\n🎼 RESONANCE NETWORK ACTIVATES\n");

        let mut network = ResonanceNetwork::new();

        // Add nodes
        network.add("Heart", 1.0);
        network.add("Mind", 2.0);
        network.add("Spirit", 1.5);

        // Connect
        network.connect("Heart", "Mind", 0.8);
        network.connect("Mind", "Spirit", 0.7);
        network.connect("Spirit", "Heart", 0.9);

        // Propagate until synchronized
        for i in 0..20 {
            network.propagate();
            if i % 5 == 0 {
                println!("Cycle {}: {}", i, network.express());
            }
        }

        println!("\nFinal state: {}", network.express());
    }
}
