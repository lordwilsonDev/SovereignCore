use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bid {
    pub agent_id: Uuid,
    pub amount: f64,
}

impl PartialEq for Bid {
    fn eq(&self, other: &Self) -> bool {
        self.amount == other.amount && self.agent_id == other.agent_id
    }
}

impl PartialOrd for Bid {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.amount.partial_cmp(&other.amount)
    }
}

pub struct AuctionHouse {
    pub current_bids: Vec<Bid>,
}

impl AuctionHouse {
    pub fn new() -> Self {
        Self {
            current_bids: Vec::new(),
        }
    }

    pub fn place_bid(&mut self, bid: Bid) {
        self.current_bids.push(bid);
    }

    pub fn finalize_auction(&mut self, slot_count: usize) -> Vec<Uuid> {
        self.current_bids
            .sort_by(|a, b| b.amount.partial_cmp(&a.amount).unwrap_or(Ordering::Equal));

        let winners: Vec<Uuid> = self
            .current_bids
            .iter()
            .take(slot_count)
            .map(|b| b.agent_id)
            .collect();

        self.current_bids.clear();
        winners
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_highest_bid_wins() {
        let mut ah = AuctionHouse::new();
        let id1 = Uuid::new_v4();
        let id2 = Uuid::new_v4();
        let id3 = Uuid::new_v4();

        ah.place_bid(Bid {
            agent_id: id1,
            amount: 10.0,
        });
        ah.place_bid(Bid {
            agent_id: id2,
            amount: 20.0,
        });
        ah.place_bid(Bid {
            agent_id: id3,
            amount: 15.0,
        });

        let winners = ah.finalize_auction(2);
        assert_eq!(winners.len(), 2);
        assert_eq!(winners[0], id2);
        assert_eq!(winners[1], id3);
    }
}
