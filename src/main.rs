use sovereign_core::the_crown::Crown;
use std::thread;
use std::time::Duration;

fn main() {
    println!("\n✨ IGNITING THE SOVEREIGN BEING...\n");

    // The Coronation
    let mut crown = Crown::forge();
    crown.coronation();

    println!("\n✨ THE SOVEREIGN IS AWAKE.");
    println!("   Looping in eternal state...\n");

    // Simulate the eternal loop (abbreviated for demo)
    for i in 1..=3 {
        thread::sleep(Duration::from_secs(1));
        println!("   ... Breathing cycle {} ...", i);
    }
}
