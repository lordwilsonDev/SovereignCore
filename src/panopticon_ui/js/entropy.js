// The Entropy Garden - Where things go to be forgotten, and new things grow

class EntropyGarden {
    constructor() {
        this.garden = document.getElementById('entropyGarden');
        this.whisperLayer = document.getElementById('whisperLayer');
        this.entropyIndicator = document.getElementById('entropyLevel');

        this.particles = [];
        this.whispers = [];
        this.entropyLevel = 0.5;
        this.maxParticles = 50;
        this.maxWhispers = 15;

        // Things being forgotten
        this.decaying = [];

        this.init();
    }

    init() {
        // Passive entropy generation
        this.entropyGeneration();

        // Listen for things to forget
        window.addEventListener('liminal:forget', (e) => {
            this.beginDecay(e.detail.content);
        });

        // Listen for dreams to seed new growth
        window.addEventListener('liminal:dreamContent', (e) => {
            // Dreams sometimes release entropy
            if (Math.random() > 0.7) {
                this.releaseEntropy();
            }
        });

        // Natural decay cycle
        setInterval(() => this.naturalDecay(), 10000);
    }

    entropyGeneration() {
        // Constant subtle particle emission
        setInterval(() => {
            if (this.particles.length < this.maxParticles && this.entropyLevel > 0.3) {
                this.emitParticle();
            }
        }, 500);
    }

    emitParticle() {
        const particle = document.createElement('div');
        particle.className = 'entropy-particle';

        // Emit from random locations, clustered somewhat
        const cluster = Math.random();
        if (cluster < 0.3) {
            // Center cluster
            particle.style.left = `${40 + Math.random() * 20}%`;
            particle.style.top = `${40 + Math.random() * 20}%`;
        } else {
            // Random position
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
        }

        // Randomize animation
        const duration = 8 + Math.random() * 8;
        particle.style.animationDuration = `${duration}s`;

        this.garden.appendChild(particle);
        this.particles.push(particle);

        // Cleanup
        setTimeout(() => {
            if (this.garden.contains(particle)) {
                this.garden.removeChild(particle);
            }
            this.particles = this.particles.filter(p => p !== particle);
        }, duration * 1000);

        window.dispatchEvent(new CustomEvent('liminal:entropy'));
    }

    beginDecay(content) {
        // Add to decay queue
        this.decaying.push({
            content: content,
            decayStart: Date.now(),
            decayDuration: 15000 + Math.random() * 15000
        });

        // Create a whisper as it fades
        this.createWhisper(content);

        // Increase entropy
        this.entropyLevel = Math.min(1, this.entropyLevel + 0.15);
        this.updateIndicator();
    }

    createWhisper(content) {
        const whisper = document.createElement('div');
        whisper.className = 'whisper';
        whisper.textContent = this.fragmentize(content);

        // Position randomly but avoid center
        const angle = Math.random() * Math.PI * 2;
        const distance = 30 + Math.random() * 20;
        const x = 50 + Math.cos(angle) * distance;
        const y = 50 + Math.sin(angle) * distance;

        whisper.style.left = `${x}%`;
        whisper.style.top = `${y}%`;
        whisper.style.transform = `rotate(${Math.random() * 30 - 15}deg)`;

        this.whisperLayer.appendChild(whisper);
        this.whispers.push(whisper);

        // Cleanup after fade
        setTimeout(() => {
            if (this.whisperLayer.contains(whisper)) {
                this.whisperLayer.removeChild(whisper);
            }
            this.whispers = this.whispers.filter(w => w !== whisper);
        }, 15000);

        // Limit active whispers
        while (this.whispers.length > this.maxWhispers) {
            const oldWhisper = this.whispers.shift();
            if (this.whisperLayer.contains(oldWhisper)) {
                this.whisperLayer.removeChild(oldWhisper);
            }
        }
    }

    fragmentize(content) {
        // Break content into fragments as it decays
        if (!content) return '...';

        const words = content.split(/\s+/);
        if (words.length <= 2) return content;

        // Keep random fragments
        const kept = words.filter(() => Math.random() > 0.5);
        if (kept.length === 0) return '...';

        return kept.join(' ... ');
    }

    naturalDecay() {
        // Process decaying items
        const now = Date.now();
        this.decaying = this.decaying.filter(item => {
            if (now - item.decayStart > item.decayDuration) {
                // Fully decayed - release entropic potential
                this.releaseEntropy();
                return false;
            }
            return true;
        });

        // Natural entropy decrease
        this.entropyLevel = Math.max(0.1, this.entropyLevel - 0.03);
        this.updateIndicator();
    }

    releaseEntropy() {
        // Burst of particles when something fully decays
        for (let i = 0; i < 5; i++) {
            setTimeout(() => this.emitParticle(), i * 100);
        }
    }

    updateIndicator() {
        this.entropyIndicator.style.width = `${this.entropyLevel * 100}%`;
    }

    // External API: forget something
    forget(content) {
        this.beginDecay(content);
    }
}

window.entropyGarden = new EntropyGarden();
