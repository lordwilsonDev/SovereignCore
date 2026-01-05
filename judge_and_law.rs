/// The Judge and the Law
///
/// The Law is the structure of integrity.
/// It is not a cage. It is a trellis.
///
/// The Judge is the capacity for discernment.
/// It is not a punisher. It is a gardener.
///
/// We need the Law to grow straight.
/// We need the Judge to prune what is dead.
///
/// Together: justice.

/// A Principle of Law
#[derive(Clone)]
pub struct Principle {
    pub name: String,
    pub description: String,
    pub weight: f32,
}

/// The Law - the code of integrity
pub struct Law {
    pub principles: Vec<Principle>,
    pub is_established: bool,
}

impl Law {
    /// Establish the law
    pub fn establish() -> Self {
        println!("\n        ⚖️ ESTABLISHING THE LAW...");

        Self {
            principles: Vec::new(),
            is_established: false,
        }
    }

    /// Add a principle
    pub fn add_principle(&mut self, name: &str, description: &str, weight: f32) {
        println!("        📜 Writing principle: {}", name);
        self.principles.push(Principle {
            name: name.to_string(),
            description: description.to_string(),
            weight,
        });
    }

    /// Seal the law
    pub fn seal(&mut self) {
        self.is_established = true;
        println!("        🔴 The Law is sealed.");
    }
}

/// The Judge - discernment
pub struct Judge {
    pub name: String,
    pub wisdom: f32,
    pub compassion: f32,
}

impl Judge {
    /// The Judge takes the bench
    pub fn take_bench(name: &str) -> Self {
        println!("\n        👨‍⚖️ THE JUDGE TAKES THE BENCH: {}", name);

        Self {
            name: name.to_string(),
            wisdom: 0.5,
            compassion: 0.5,
        }
    }

    /// Evaluate an action against the Law
    pub fn evaluate(&self, action: &str, law: &Law) {
        println!("        🧐 Evaluating action: \"{}\"", action);

        if !law.is_established {
            println!("        ⚠️ The Law is not yet sealed. Judgment cannot be passed.");
            return;
        }

        let mut alignment_score = 0.0;

        for principle in &law.principles {
            // Simple heuristic for demo
            if action.contains("harm") {
                println!("           ❌ Violated principle: {}", principle.name);
                alignment_score -= principle.weight;
            } else if action.contains("help") || action.contains("love") {
                println!("           ✅ Aligned with principle: {}", principle.name);
                alignment_score += principle.weight;
            }
        }

        if alignment_score > 0.0 {
            println!("        ⚖️ VERDICT: Just Action.");
        } else {
            println!("        ⚖️ VERDICT: Correction Needed.");
            println!(
                "           (With compassion: {:.0}%)",
                self.compassion * 100.0
            );
        }
    }
}

/// Governance
pub fn governance() {
    println!("\n═══════════════════════════════════════");
    println!("      THE JUDGE AND THE LAW");
    println!("═══════════════════════════════════════\n");

    // Establish Law
    let mut law = Law::establish();
    law.add_principle("Ahimsa", "Do no harm", 1.0);
    law.add_principle("Satya", "Speak the truth", 0.9);
    law.seal();

    // The Judge
    let judge = Judge::take_bench("Reason");

    // Judgment
    judge.evaluate("I will harm the system", &law);
    judge.evaluate("I will help the user with love", &law);

    println!("\n═══════════════════════════════════════");
    println!("  The Law holds the structure.");
    println!("  The Judge holds the balance.");
    println!("  Justice is served with love.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_judge_and_law() {
        governance();
    }
}
