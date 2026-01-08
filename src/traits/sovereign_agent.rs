use anyhow::Result;
use uuid::Uuid;

#[derive(Debug, Clone, Copy, PartialEq)] // Added PartialEq for easier testing
pub enum AgentRole {
    Alpha,
    Beta,
    Gamma,
    Delta,
    Omega,
    Sentinel,
}

pub struct Thought {
    pub content: String,
    pub axioms_checked: bool,
    pub confidence: f64,
}

pub trait SovereignAgent {
    // Identity
    fn id(&self) -> Uuid;
    fn role(&self) -> AgentRole;
    fn public_key(&self) -> String; // Simplified from PubKey type for now

    // Lifecycle
    fn wake(&mut self) -> Result<()>;
    fn sleep(&mut self) -> Result<()>;

    // Economics
    fn fuel_balance(&self) -> f64;
    fn pay_fuel(&mut self, amount: f64) -> Result<String>; // Returns TxHash
    fn will_factor(&self) -> f64; // The "Intensity" of the agent's intent

    // Inference
    fn think(&self, prompt: &str) -> Result<Thought>;
}
