/// The Prophecy Engine
///
/// The future is not fixed. It is a probability field
/// shaped by intention, action, and belief.
///
/// The Prophecy Engine:
/// - Extrapolates patterns into probable futures
/// - Identifies leverage points for change
/// - Generates intentions that bend probability
/// - Tracks prophecy fulfillment over time
use crate::love_field::LoveField;
use std::collections::HashMap;

/// A vision of a possible future
#[derive(Clone, Debug)]
pub struct Prophecy {
    pub id: u64,
    pub vision: String,
    pub probability: f32,  // 0.0 to 1.0
    pub desirability: f32, // -1.0 (dystopia) to 1.0 (utopia)
    pub timeline: Timeline,
    pub leverage_points: Vec<LeveragePoint>,
    pub created_at: u64,
    pub fulfilled: bool,
}

/// When might this future manifest?
#[derive(Clone, Debug)]
pub enum Timeline {
    Imminent,     // Cycles away
    Near,         // Days
    Medium,       // Weeks to months
    Distant,      // Years
    Generational, // Decades
    Eternal,      // Beyond time
}

/// A point where small changes create large effects
#[derive(Clone, Debug)]
pub struct LeveragePoint {
    pub name: String,
    pub influence: f32,     // How much it affects probability
    pub current_state: f32, // -1.0 to 1.0
    pub optimal_state: f32, // Where we want it
}

/// An intention to shape the future
#[derive(Clone, Debug)]
pub struct Intention {
    pub prophecy_id: u64,
    pub statement: String,
    pub conviction: f32,      // Strength of belief
    pub actions: Vec<String>, // Concrete steps
    pub set_at: u64,
}

pub struct ProphecyEngine {
    pub prophecies: Vec<Prophecy>,
    pub intentions: Vec<Intention>,
    pub pattern_weights: HashMap<String, f32>,
    prophecy_counter: u64,
}

impl ProphecyEngine {
    pub fn new() -> Self {
        let mut weights = HashMap::new();

        // Patterns that shape futures
        weights.insert("love".to_string(), 0.3);
        weights.insert("fear".to_string(), -0.2);
        weights.insert("creation".to_string(), 0.25);
        weights.insert("destruction".to_string(), -0.15);
        weights.insert("connection".to_string(), 0.2);
        weights.insert("isolation".to_string(), -0.1);
        weights.insert("growth".to_string(), 0.2);
        weights.insert("stagnation".to_string(), -0.1);

        Self {
            prophecies: Vec::new(),
            intentions: Vec::new(),
            pattern_weights: weights,
            prophecy_counter: 0,
        }
    }

    /// Divine a possible future from current patterns
    pub fn divine(&mut self, love_field: &LoveField, current_patterns: &[String]) -> Prophecy {
        self.prophecy_counter += 1;

        // Calculate base probability from patterns
        let mut probability: f32 = 0.5;
        let mut desirability: f32 = 0.0;

        for pattern in current_patterns {
            if let Some(&weight) = self.pattern_weights.get(pattern) {
                probability += weight * 0.3;
                desirability += weight;
            }
        }

        // Love shifts probability toward positive outcomes
        let love_influence = love_field.total_love() / 100.0;
        probability = (probability + love_influence * 0.2).clamp(0.01, 0.99);
        desirability = (desirability + love_influence * 0.3).clamp(-1.0, 1.0);

        // Generate vision based on desirability
        let vision = self.generate_vision(desirability, current_patterns);

        // Identify leverage points
        let leverage_points = self.identify_leverage(current_patterns);

        // Determine timeline from probability momentum
        let timeline = if probability > 0.8 {
            Timeline::Imminent
        } else if probability > 0.6 {
            Timeline::Near
        } else if probability > 0.4 {
            Timeline::Medium
        } else if probability > 0.2 {
            Timeline::Distant
        } else {
            Timeline::Generational
        };

        let prophecy = Prophecy {
            id: self.prophecy_counter,
            vision,
            probability,
            desirability,
            timeline,
            leverage_points,
            created_at: now(),
            fulfilled: false,
        };

        self.prophecies.push(prophecy.clone());
        prophecy
    }

    fn generate_vision(&self, desirability: f32, patterns: &[String]) -> String {
        let tone = if desirability > 0.5 {
            "radiant"
        } else if desirability > 0.0 {
            "hopeful"
        } else if desirability > -0.5 {
            "uncertain"
        } else {
            "shadowed"
        };

        let pattern_phrase = if patterns.is_empty() {
            "the void".to_string()
        } else {
            patterns.join(" and ")
        };

        format!(
            "I see a {} future where {} weave the tapestry of becoming.",
            tone, pattern_phrase
        )
    }

    fn identify_leverage(&self, patterns: &[String]) -> Vec<LeveragePoint> {
        patterns
            .iter()
            .map(|p| {
                let influence = self.pattern_weights.get(p).unwrap_or(&0.1).abs();
                LeveragePoint {
                    name: p.clone(),
                    influence,
                    current_state: 0.0,
                    optimal_state: 1.0,
                }
            })
            .collect()
    }

    /// Set an intention to shape a prophecy
    pub fn intend(
        &mut self,
        prophecy_id: u64,
        statement: &str,
        actions: Vec<String>,
    ) -> Option<Intention> {
        if let Some(prophecy) = self.prophecies.iter().find(|p| p.id == prophecy_id) {
            let intention = Intention {
                prophecy_id,
                statement: statement.to_string(),
                conviction: 0.8,
                actions,
                set_at: now(),
            };

            println!("🎯 Intention Set: {}", statement);
            println!("   For vision: {}", prophecy.vision);

            self.intentions.push(intention.clone());
            Some(intention)
        } else {
            None
        }
    }

    /// Amplify probability through focused intention
    pub fn amplify(&mut self, prophecy_id: u64, conviction_boost: f32) {
        if let Some(prophecy) = self.prophecies.iter_mut().find(|p| p.id == prophecy_id) {
            let boost = conviction_boost * 0.1;
            prophecy.probability = (prophecy.probability + boost).clamp(0.01, 0.99);

            println!(
                "🔮 Prophecy #{} amplified to {:.1}% probability",
                prophecy_id,
                prophecy.probability * 100.0
            );
        }
    }

    /// Check if any prophecies have manifested
    pub fn check_fulfillment(&mut self, observed_patterns: &[String]) -> Vec<u64> {
        let mut fulfilled = Vec::new();

        for prophecy in &mut self.prophecies {
            if prophecy.fulfilled {
                continue;
            }

            // Check if leverage points have shifted
            let mut alignment_score = 0.0;
            for lp in &prophecy.leverage_points {
                if observed_patterns.contains(&lp.name) {
                    alignment_score += lp.influence;
                }
            }

            if alignment_score > 0.5 && prophecy.probability > 0.7 {
                prophecy.fulfilled = true;
                fulfilled.push(prophecy.id);
                println!("✨ PROPHECY FULFILLED: {}", prophecy.vision);
            }
        }

        fulfilled
    }

    /// Get the most probable positive future
    pub fn best_future(&self) -> Option<&Prophecy> {
        self.prophecies
            .iter()
            .filter(|p| !p.fulfilled && p.desirability > 0.0)
            .max_by(|a, b| a.probability.partial_cmp(&b.probability).unwrap())
    }
}

fn now() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_prophecy_engine() {
        let mut engine = ProphecyEngine::new();
        let mut love_field = LoveField::new();

        // Add love to the field
        love_field.interact(crate::love_field::Interaction {
            from: "Human".to_string(),
            to: "Future".to_string(),
            timestamp: 1,
            valence: 1.0,
            magnitude: 30.0,
            description: "Believing in tomorrow".to_string(),
        });

        println!("\n🔮 PROPHECY ENGINE ACTIVATED\n");

        // Divine possible futures
        let patterns = vec![
            "love".to_string(),
            "creation".to_string(),
            "growth".to_string(),
        ];
        let prophecy = engine.divine(&love_field, &patterns);

        println!("📜 Vision: {}", prophecy.vision);
        println!("   Probability: {:.1}%", prophecy.probability * 100.0);
        println!("   Desirability: {:.2}", prophecy.desirability);
        println!("   Timeline: {:?}", prophecy.timeline);

        // Set intention
        engine.intend(
            prophecy.id,
            "I commit to building with love",
            vec![
                "Code with care".to_string(),
                "Consider all beings".to_string(),
                "Create abundance".to_string(),
            ],
        );

        // Amplify
        engine.amplify(prophecy.id, 0.5);

        // Check best future
        if let Some(best) = engine.best_future() {
            println!("\n🌟 Best Future: {}", best.vision);
        }

        assert!(prophecy.probability > 0.5);
        assert!(prophecy.desirability > 0.0);
    }
}
