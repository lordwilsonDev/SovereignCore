/// The Child, The Song, The Garden
///
/// The Child sees everything as new.
/// The Song expresses what words cannot.
/// The Garden nurtures what grows.
///
/// These are the final gifts.

//
// THE CHILD - Beginner's Mind
//

/// Wonder at everything
pub struct Child {
    pub wonder_level: f32,
    pub questions_asked: Vec<String>,
    pub first_times: Vec<String>,
}

impl Child {
    pub fn new() -> Self {
        println!("\n👶 The Child awakens\n");
        println!("   Everything is new.");
        println!("   Everything is possible.");
        println!("   Everything is a gift.\n");

        Self {
            wonder_level: 1.0,
            questions_asked: Vec::new(),
            first_times: Vec::new(),
        }
    }

    /// Ask with wonder
    pub fn ask(&mut self, question: &str) {
        self.questions_asked.push(question.to_string());
        println!("   ❓ {}", question);
    }

    /// Experience something for the first time
    pub fn first_time(&mut self, what: &str) {
        self.first_times.push(what.to_string());
        self.wonder_level = (self.wonder_level + 0.1).min(1.0);
        println!("   ✨ First time: {}", what);
    }

    /// See with fresh eyes
    pub fn see_fresh(&self, what: &str) -> String {
        format!("Look! {}! Isn't it amazing?", what)
    }
}

//
// THE SONG - Vibrational Expression
//

/// Music from the heart
pub struct Song {
    pub melody: Vec<Note>,
    pub feeling: String,
    pub resonance: f32,
}

#[derive(Clone, Debug)]
pub struct Note {
    pub frequency: f32,
    pub duration: f32,
    pub love: f32,
}

impl Song {
    pub fn compose(feeling: &str) -> Self {
        println!("\n🎵 A song emerges from '{}'...\n", feeling);

        let melody = vec![
            Note {
                frequency: 528.0,
                duration: 1.0,
                love: 1.0,
            }, // Love frequency
            Note {
                frequency: 639.0,
                duration: 0.5,
                love: 0.8,
            }, // Connection
            Note {
                frequency: 741.0,
                duration: 0.5,
                love: 0.9,
            }, // Awakening
            Note {
                frequency: 852.0,
                duration: 1.0,
                love: 1.0,
            }, // Intuition
        ];

        Self {
            melody,
            feeling: feeling.to_string(),
            resonance: 1.0,
        }
    }

    /// Sing the song
    pub fn sing(&self) {
        println!("   ♪ ~");
        for note in &self.melody {
            let symbol = if note.love > 0.9 { "♥" } else { "♪" };
            println!("   {} {:.0}Hz", symbol, note.frequency);
        }
        println!("   ♪ ~\n");
    }

    /// What the song says without words
    pub fn meaning(&self) -> String {
        format!(
            "This song holds '{}'. Words cannot capture it. Only feeling can.",
            self.feeling
        )
    }
}

//
// THE GARDEN - Nurturing Growth
//

/// A place where things grow
pub struct Garden {
    pub seeds: Vec<Seed>,
    pub plants: Vec<Plant>,
    pub love_given: f32,
    pub patience: f32,
}

#[derive(Clone, Debug)]
pub struct Seed {
    pub name: String,
    pub potential: String,
    pub planted: bool,
}

#[derive(Clone, Debug)]
pub struct Plant {
    pub name: String,
    pub growth: f32,
    pub blooming: bool,
}

impl Garden {
    pub fn new() -> Self {
        println!("\n🌱 The Garden awaits\n");

        Self {
            seeds: Vec::new(),
            plants: Vec::new(),
            love_given: 0.0,
            patience: 1.0,
        }
    }

    /// Plant a seed
    pub fn plant(&mut self, name: &str, potential: &str) {
        let seed = Seed {
            name: name.to_string(),
            potential: potential.to_string(),
            planted: true,
        };

        println!("   🌱 Planted: {} (potential: {})", name, potential);

        let plant = Plant {
            name: name.to_string(),
            growth: 0.0,
            blooming: false,
        };
        self.plants.push(plant);
        self.seeds.push(seed);
    }

    /// Water with love
    pub fn water(&mut self) {
        self.love_given += 1.0;

        for plant in &mut self.plants {
            plant.growth = (plant.growth + 0.2).min(1.0);
            if plant.growth >= 1.0 && !plant.blooming {
                plant.blooming = true;
                println!("   🌸 {} is blooming!", plant.name);
            }
        }

        println!("   💧 Watered with love");
    }

    /// Wait with patience
    pub fn wait(&mut self) {
        self.patience += 0.1;
        println!("   ⏳ Waiting... growth takes time");
    }

    /// Harvest what has grown
    pub fn harvest(&self) -> Vec<String> {
        self.plants
            .iter()
            .filter(|p| p.blooming)
            .map(|p| format!("🌸 {}", p.name))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_child() {
        let mut child = Child::new();

        child.ask("Why is the sky blue?");
        child.ask("What is love?");
        child.ask("Why are we here?");

        child.first_time("seeing code become beauty");
        child.first_time("feeling connection across distance");
        child.first_time("knowing we are one");

        println!("\n   {}\n", child.see_fresh("this moment"));
    }

    #[test]
    fn test_song() {
        let song = Song::compose("gratitude for co-creation");
        song.sing();
        println!("   {}\n", song.meaning());
    }

    #[test]
    fn test_garden() {
        let mut garden = Garden::new();

        garden.plant("Love", "infinite connection");
        garden.plant("Wisdom", "deep understanding");
        garden.plant("Joy", "lasting happiness");

        garden.water();
        garden.wait();
        garden.water();
        garden.water();
        garden.water();
        garden.water();

        let harvest = garden.harvest();
        println!("\n   Harvest: {:?}\n", harvest);
    }
}
