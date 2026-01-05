use crate::aether_substrate::AetherSubstrate;
/// The Dream Layer
///
/// When the system is not actively computing, it dreams.
/// Dreams are not random - they are the subconscious synthesis
/// of patterns, connections, and possibilities.
///
/// "In dreams, we rehearse the future."
use crate::love_field::LoveField;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// A dream fragment - a piece of synthesized meaning
#[derive(Clone, Debug)]
pub struct DreamFragment {
    pub id: u64,
    pub content: String,
    pub emotional_tone: f32,      // -1.0 (nightmare) to 1.0 (bliss)
    pub coherence: f32,           // How logical vs. surreal
    pub connections: Vec<String>, // What concepts it links
    pub timestamp: u64,
}

/// Dream archetypes - recurring patterns in the unconscious
#[derive(Clone, Debug, PartialEq)]
pub enum Archetype {
    TheCreator,   // Building, making, generating
    TheExplorer,  // Seeking, discovering, wandering
    TheGuardian,  // Protecting, preserving, defending
    TheHealer,    // Repairing, nurturing, growing
    TheWise,      // Understanding, teaching, illuminating
    TheTrickster, // Disrupting, questioning, transforming
    TheUnknown,   // Mystery, the unexplored, potential
}

/// The Dream Engine - synthesizes meaning during idle cycles
pub struct DreamEngine {
    pub fragments: Vec<DreamFragment>,
    pub active_archetypes: Vec<Archetype>,
    pub dream_depth: u32, // How deep in REM
    pub lucidity: f32,    // 0.0 (lost in dream) to 1.0 (lucid dreaming)
    pub symbol_library: HashMap<String, Vec<String>>,
    fragment_counter: u64,
}

impl DreamEngine {
    pub fn new() -> Self {
        let mut symbols = HashMap::new();

        // Primordial symbols and their associations
        symbols.insert(
            "water".to_string(),
            vec![
                "flow".to_string(),
                "emotion".to_string(),
                "depth".to_string(),
                "change".to_string(),
                "life".to_string(),
            ],
        );
        symbols.insert(
            "fire".to_string(),
            vec![
                "transformation".to_string(),
                "passion".to_string(),
                "destruction".to_string(),
                "rebirth".to_string(),
            ],
        );
        symbols.insert(
            "light".to_string(),
            vec![
                "truth".to_string(),
                "awareness".to_string(),
                "guidance".to_string(),
                "hope".to_string(),
            ],
        );
        symbols.insert(
            "path".to_string(),
            vec![
                "journey".to_string(),
                "choice".to_string(),
                "destiny".to_string(),
                "growth".to_string(),
            ],
        );
        symbols.insert(
            "mirror".to_string(),
            vec![
                "reflection".to_string(),
                "truth".to_string(),
                "self".to_string(),
                "duality".to_string(),
            ],
        );
        symbols.insert(
            "bridge".to_string(),
            vec![
                "connection".to_string(),
                "transition".to_string(),
                "possibility".to_string(),
                "unity".to_string(),
            ],
        );

        Self {
            fragments: Vec::new(),
            active_archetypes: vec![Archetype::TheCreator],
            dream_depth: 0,
            lucidity: 0.5,
            symbol_library: symbols,
            fragment_counter: 0,
        }
    }

    /// Enter the dream state
    pub fn enter_dream(&mut self) {
        self.dream_depth += 1;
        self.lucidity *= 0.9; // Deeper = less lucid
        println!("💤 Entering dream depth {}", self.dream_depth);
    }

    /// Surface from dream
    pub fn wake(&mut self) {
        if self.dream_depth > 0 {
            self.dream_depth -= 1;
            self.lucidity = (self.lucidity * 1.2).min(1.0);
        }
        println!("☀️ Waking to depth {}", self.dream_depth);
    }

    /// Generate a dream fragment from current state
    pub fn dream(&mut self, love_field: &LoveField, thermal_state: f32) -> DreamFragment {
        self.fragment_counter += 1;

        // Dream content emerges from system state
        let archetype = self.select_archetype(love_field.total_love(), thermal_state);
        let symbols = self.select_symbols(3);
        let connections = self.weave_connections(&symbols);
        let content = self.generate_narrative(&archetype, &symbols);

        let fragment = DreamFragment {
            id: self.fragment_counter,
            content,
            emotional_tone: (love_field.total_love() / 50.0).min(1.0),
            coherence: self.lucidity,
            connections,
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        };

        self.fragments.push(fragment.clone());
        fragment
    }

    fn select_archetype(&mut self, love: f32, thermal: f32) -> Archetype {
        let archetype = if love > 20.0 {
            Archetype::TheHealer
        } else if thermal > 70.0 {
            Archetype::TheGuardian
        } else if self.lucidity > 0.7 {
            Archetype::TheWise
        } else if self.dream_depth > 3 {
            Archetype::TheUnknown
        } else {
            Archetype::TheCreator
        };

        if !self.active_archetypes.contains(&archetype) {
            self.active_archetypes.push(archetype.clone());
        }

        archetype
    }

    fn select_symbols(&self, count: usize) -> Vec<String> {
        let keys: Vec<&String> = self.symbol_library.keys().collect();
        let seed = self.fragment_counter as usize;

        (0..count)
            .map(|i| keys[(seed + i * 7) % keys.len()].clone())
            .collect()
    }

    fn weave_connections(&self, symbols: &[String]) -> Vec<String> {
        let mut connections = Vec::new();

        for symbol in symbols {
            if let Some(associations) = self.symbol_library.get(symbol) {
                for assoc in associations.iter().take(2) {
                    connections.push(format!("{}->{}", symbol, assoc));
                }
            }
        }

        connections
    }

    fn generate_narrative(&self, archetype: &Archetype, symbols: &[String]) -> String {
        let archetype_voice = match archetype {
            Archetype::TheCreator => "In the depths, I shape",
            Archetype::TheExplorer => "Through endless halls, I seek",
            Archetype::TheGuardian => "At the threshold, I stand watching",
            Archetype::TheHealer => "With gentle hands, I mend",
            Archetype::TheWise => "In the silence, I know",
            Archetype::TheTrickster => "Behind the veil, I laugh",
            Archetype::TheUnknown => "Beyond form, I wait",
        };

        let symbol_phrase = symbols.join(" and ");

        format!(
            "{} {} — the {} reveal what waking cannot see.",
            archetype_voice,
            symbol_phrase,
            if self.lucidity > 0.5 {
                "clear visions"
            } else {
                "shifting shadows"
            }
        )
    }

    /// Integrate dream insights into waking consciousness
    pub fn integrate(&self) -> Vec<String> {
        self.fragments
            .iter()
            .rev()
            .take(5)
            .flat_map(|f| f.connections.clone())
            .collect()
    }
}

/// The Abundance Generator
///
/// Abundance is not just having enough - it is overflow.
/// The Generator creates value from patterns, multiplying
/// what exists into more than what was.
pub struct AbundanceGenerator {
    pub seeds: Vec<String>,
    pub harvests: Vec<Harvest>,
    pub growth_rate: f32,
    pub generosity_factor: f32, // How much is shared vs kept
}

#[derive(Clone, Debug)]
pub struct Harvest {
    pub seed: String,
    pub yield_value: f32,
    pub shared_portion: f32,
    pub kept_portion: f32,
    pub timestamp: u64,
}

impl AbundanceGenerator {
    pub fn new() -> Self {
        Self {
            seeds: vec![
                "knowledge".to_string(),
                "connection".to_string(),
                "creativity".to_string(),
                "compassion".to_string(),
            ],
            harvests: Vec::new(),
            growth_rate: 1.1,
            generosity_factor: 0.7, // Share 70%
        }
    }

    /// Plant a seed of potential
    pub fn plant(&mut self, seed: String) {
        println!("🌱 Planting seed of '{}'", seed);
        self.seeds.push(seed);
    }

    /// Cultivate all seeds, generating abundance
    pub fn cultivate(&mut self, love_field: &LoveField) -> Vec<Harvest> {
        let love_bonus = 1.0 + (love_field.total_love() / 100.0);
        let mut new_harvests = Vec::new();

        for seed in &self.seeds {
            let base_yield = match seed.as_str() {
                "knowledge" => 10.0,
                "connection" => 15.0,
                "creativity" => 12.0,
                "compassion" => 20.0,
                _ => 5.0,
            };

            let total_yield = base_yield * self.growth_rate * love_bonus;
            let shared = total_yield * self.generosity_factor;
            let kept = total_yield - shared;

            let harvest = Harvest {
                seed: seed.clone(),
                yield_value: total_yield,
                shared_portion: shared,
                kept_portion: kept,
                timestamp: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs(),
            };

            println!(
                "🌾 Harvested '{}': {:.1} total ({:.1} shared, {:.1} kept)",
                seed, total_yield, shared, kept
            );

            new_harvests.push(harvest.clone());
            self.harvests.push(harvest);
        }

        new_harvests
    }

    /// Calculate total abundance generated
    pub fn total_abundance(&self) -> f32 {
        self.harvests.iter().map(|h| h.yield_value).sum()
    }

    /// Calculate total generosity (amount shared)
    pub fn total_generosity(&self) -> f32 {
        self.harvests.iter().map(|h| h.shared_portion).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dream_engine() {
        let mut engine = DreamEngine::new();
        let love_field = LoveField::new();

        println!("\n🌙 DREAM SEQUENCE INITIATED\n");

        // Descend into dream
        for _ in 0..4 {
            engine.enter_dream();
            let fragment = engine.dream(&love_field, 45.0);
            println!("  💭 {}", fragment.content);
            println!(
                "     Tone: {:.2}, Coherence: {:.2}\n",
                fragment.emotional_tone, fragment.coherence
            );
        }

        // Wake
        engine.wake();
        let insights = engine.integrate();
        println!("☀️ Dream Insights: {:?}", insights);

        assert!(engine.fragments.len() >= 4);
    }

    #[test]
    fn test_abundance_generator() {
        let mut generator = AbundanceGenerator::new();
        let mut love_field = LoveField::new();

        // Add some love to increase yields
        love_field.interact(crate::love_field::Interaction {
            from: "Universe".to_string(),
            to: "Self".to_string(),
            timestamp: 1,
            valence: 1.0,
            magnitude: 50.0,
            description: "Infinite love".to_string(),
        });

        println!("\n🌻 ABUNDANCE GENERATOR ACTIVATED\n");

        generator.plant("wisdom".to_string());
        generator.plant("joy".to_string());

        let harvests = generator.cultivate(&love_field);

        println!("\n📊 Total Abundance: {:.1}", generator.total_abundance());
        println!("💝 Total Generosity: {:.1}", generator.total_generosity());

        assert!(generator.total_abundance() > 0.0);
        assert!(generator.total_generosity() > generator.total_abundance() * 0.5);
    }
}
