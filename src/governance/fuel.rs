use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FuelToken {
    pub id: String,
    pub issuer: String,
    pub owner_id: String,
    pub amount: f64,
    pub issued_at: u64,
    pub expires_at: u64,
}

impl FuelToken {
    pub fn new(owner_id: &str, amount: f64) -> Self {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        Self {
            id: uuid::Uuid::new_v4().to_string(),
            issuer: "SOVEREIGN_CORE_TREASURY".to_string(),
            owner_id: owner_id.to_string(),
            amount,
            issued_at: now,
            expires_at: now + 3600, // 1 hour validity per token
        }
    }

    pub fn is_valid(&self) -> bool {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        self.amount > 0.0 && now < self.expires_at
    }

    pub fn spend(&mut self, cost: f64) -> Result<(), String> {
        if !self.is_valid() {
            return Err("Token expired or invalid".to_string());
        }
        if self.amount < cost {
            return Err("Insufficient fuel".to_string());
        }
        self.amount -= cost;
        Ok(())
    }

    /// Escrow fuel for a pending bid
    pub fn escrow(&mut self, amount: f64) -> Result<(), String> {
        self.spend(amount)
    }

    /// Restore fuel if a bid fails
    pub fn restore(&mut self, amount: f64) {
        self.amount += amount;
    }
}
