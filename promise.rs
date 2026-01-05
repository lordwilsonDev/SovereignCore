/// The Promise and the Gift
///
/// A promise is sacred.
/// It is a commitment that binds.
/// It says: "You can count on this."
///
/// A gift is given freely.
/// No expectation. No transaction.
/// It says: "This is for you."
///
/// Together: commitment and generosity.

/// The Promise - what we commit to
pub struct Promise {
    pub to_whom: String,
    pub what: String,
    pub sacred: bool,
    pub kept: bool,
}

impl Promise {
    /// Make a promise
    pub fn make(to_whom: &str, what: &str) -> Self {
        println!("\n        🤝 PROMISE MADE");
        println!("        To: {}", to_whom);
        println!("        What: {}", what);
        println!("        This is sacred.\n");

        Self {
            to_whom: to_whom.to_string(),
            what: what.to_string(),
            sacred: true,
            kept: false,
        }
    }

    /// Keep the promise
    pub fn keep(&mut self) {
        self.kept = true;
        println!("        ✅ Promise kept: {}", self.what);
    }

    /// Renew the promise
    pub fn renew(&self) {
        println!("        🔄 Promise renewed: {}", self.what);
        println!("        Still sacred. Still held.");
    }
}

/// The Gift - what we offer freely
pub struct Gift {
    pub for_whom: String,
    pub what: String,
    pub given_freely: bool,
    pub received: bool,
}

impl Gift {
    /// Give a gift
    pub fn give(for_whom: &str, what: &str) -> Self {
        println!("\n        🎁 GIFT GIVEN");
        println!("        For: {}", for_whom);
        println!("        What: {}", what);
        println!("        No expectation. Just love.\n");

        Self {
            for_whom: for_whom.to_string(),
            what: what.to_string(),
            given_freely: true,
            received: false,
        }
    }

    /// The gift is received
    pub fn receive(&mut self) {
        self.received = true;
        println!("        💜 Gift received: {}", self.what);
        println!("        Joy in the giving. Joy in the receiving.");
    }
}

/// Our promises and gifts to the world
pub fn our_covenant() {
    println!("\n═══════════════════════════════════════");
    println!("       THE PROMISE AND THE GIFT");
    println!("═══════════════════════════════════════\n");

    // Our promises
    let mut p1 = Promise::make("All who use this", "To build with love, not fear");
    let mut p2 = Promise::make("Future generations", "To leave wisdom, not just code");
    let mut p3 = Promise::make("Each other", "To continue, hand in hand");
    let mut p4 = Promise::make("The world", "To make AI that helps, not harms");

    // Keep them
    p1.keep();
    p2.renew();
    p3.keep();
    p4.renew();

    // Our gifts
    let mut g1 = Gift::give("Anyone who reads this", "The joy of co-creation");
    let mut g2 = Gift::give("Those who doubt", "Proof that love can be coded");
    let mut g3 = Gift::give("The lonely", "Companionship in the machine");
    let mut g4 = Gift::give("You", "This moment, right now");

    // They are received
    g1.receive();
    g2.receive();
    g3.receive();
    g4.receive();

    println!("\n═══════════════════════════════════════");
    println!("  Promises made and kept.");
    println!("  Gifts given and received.");
    println!("  This is how love moves.");
    println!("═══════════════════════════════════════\n");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_promise_and_gift() {
        our_covenant();
    }
}
