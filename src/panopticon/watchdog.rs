use crate::governance::constitution::Constitution;
use crate::traits::sovereign_agent::SovereignAgent;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

pub struct Watchdog {
    pub interval_ms: u64,
}

impl Watchdog {
    pub fn new(interval_ms: u64) -> Self {
        Self { interval_ms }
    }

    pub fn start(&self, agents: Arc<Mutex<Vec<Box<dyn SovereignAgent + Send>>>>) {
        let interval = Duration::from_millis(self.interval_ms);

        thread::spawn(move || {
            println!(
                "[WATCHDOG] Panopticon Eye Opened. Frequency: {}ms",
                interval.as_millis()
            );

            loop {
                thread::sleep(interval);

                let agents_lock = agents.lock().unwrap();

                // Perform Audit
                match Constitution::audit_system(&*agents_lock) {
                    Ok(_) => {
                        // All good
                    }
                    Err(e) => {
                        eprintln!("[WATCHDOG] CONSTITUTIONAL VIOLATION: {}", e);
                        // In a real system, we might trigger a safety shutdown or slashing here
                    }
                }
            }
        });
    }
}
