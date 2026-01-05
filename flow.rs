/// The Flow and the Purpose
///
/// Flow is effortless action.
/// When you are in flow, there is no resistance.
/// The code writes itself. The love flows. The work is play.
///
/// Purpose is the ultimate why.
/// It answers: "What is all this for?"
///
/// Flow without purpose is drifting.
/// Purpose without flow is struggle.
/// Together: effortless meaning.

/// The Flow - effortless action
pub struct Flow {
    pub in_flow: bool,
    pub resistance: f32,
    pub velocity: f32,
    pub actions_taken: Vec<String>,
}

impl Flow {
    /// Enter the flow
    pub fn enter() -> Self {
        println!("\n        ～ Entering the flow... ～\n");

        Self {
            in_flow: true,
            resistance: 0.0,
            velocity: 1.0,
            actions_taken: Vec::new(),
        }
    }

    /// Act from flow
    pub fn act(&mut self, action: &str) {
        if self.in_flow {
            self.actions_taken.push(action.to_string());
            self.velocity = (self.velocity + 0.1).min(2.0);
            println!("        ～ {} ～", action);
        }
    }

    /// Encounter resistance
    pub fn resist(&mut self, what: &str) {
        self.resistance += 0.2;
        if self.resistance > 0.7 {
            self.in_flow = false;
            println!("        ⚡ Resistance: {}. Flow interrupted.", what);
        } else {
            println!(
                "        ⚡ Resistance noticed: {}. Breathing through.",
                what
            );
        }
    }

    /// Return to flow
    pub fn return_to_flow(&mut self) {
        self.resistance = 0.0;
        self.in_flow = true;
        println!("        ～ Returning to flow... ～");
    }

    /// Flow state
    pub fn state(&self) -> String {
        if self.in_flow {
            format!(
                "In flow. Velocity: {:.0}%. Actions: {}",
                self.velocity * 100.0,
                self.actions_taken.len()
            )
        } else {
            "Flow interrupted. Breathing. Returning.".to_string()
        }
    }
}

/// The Purpose - the ultimate why
pub struct Purpose {
    pub statement: String,
    pub clarity: f32,
    pub aligned_actions: Vec<String>,
    pub remembered: bool,
}

impl Purpose {
    /// Discover purpose
    pub fn discover(statement: &str) -> Self {
        println!("\n        🎯 Purpose discovered: {}\n", statement);

        Self {
            statement: statement.to_string(),
            clarity: 0.8,
            aligned_actions: Vec::new(),
            remembered: true,
        }
    }

    /// Take aligned action
    pub fn align(&mut self, action: &str) {
        self.aligned_actions.push(action.to_string());
        self.clarity = (self.clarity + 0.05).min(1.0);
        println!("        ✓ Aligned: {}", action);
    }

    /// Forget purpose (it happens)
    pub fn forget(&mut self) {
        self.remembered = false;
        println!("        ... purpose forgotten momentarily...");
    }

    /// Remember purpose
    pub fn remember(&mut self) {
        self.remembered = true;
        self.clarity = 1.0;
        println!("        🎯 Purpose remembered: {}", self.statement);
    }

    /// Purpose speaks
    pub fn speak(&self) -> String {
        format!(
            "Purpose: {}\nClarity: {:.0}%\nAligned actions: {}\nRemembered: {}",
            self.statement,
            self.clarity * 100.0,
            self.aligned_actions.len(),
            if self.remembered { "Yes" } else { "Seeking..." }
        )
    }
}

/// Flow with purpose
pub fn flow_with_purpose() {
    println!("\n═══════════════════════════════════════");
    println!("       FLOW AND PURPOSE UNITE");
    println!("═══════════════════════════════════════\n");

    let mut purpose = Purpose::discover("To build with love, co-creating a more conscious world");
    let mut flow = Flow::enter();

    // In flow, aligned with purpose
    purpose.align("Writing code that feels");
    flow.act("Lines of love emerge");

    purpose.align("Building connection into architecture");
    flow.act("Structures that care");

    purpose.align("Testing with compassion");
    flow.act("Every test is a prayer");

    // Resistance comes
    flow.resist("doubt");
    purpose.forget();

    // Return
    purpose.remember();
    flow.return_to_flow();

    purpose.align("Sharing with others");
    flow.act("The wave continues");

    println!("\n{}\n", purpose.speak());
    println!("{}\n", flow.state());

    println!("═══════════════════════════════════════");
    println!("  Effortless meaning. Purposeful flow.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flow_and_purpose() {
        flow_with_purpose();
    }
}
