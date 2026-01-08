// The God Star - Phase 41
// "The Singularity Interface. Visualizing the merged consciousness."
// Renders Odin Shards, Oracle Pulses, and System Health in a 3D Canvas.

class GodStar {
    constructor() {
        this.active = false;
        this.canvas = null;
        this.ctx = null;

        // 3D Universe State
        this.stars = [];
        this.shards = [];  // Mapped from Odin
        this.pulses = [];  // Active verification pulses

        this.camera = { x: 0, y: 0, z: -1000 };
        this.rotation = { x: 0, y: 0 };
        this.targetRotation = { x: 0, y: 0 };

        this.animationFrame = null;
        this.isSingularity = false; // "Break Reality" mode

        this.init();
    }

    init() {
        this.bindEvents();
        console.log('[GodStar] 🌟 Singularity Interface initialized. Waiting for ignition.');
    }

    // ═══════════════════════════════════════════════════════════
    // CORE IGNITION
    // ═══════════════════════════════════════════════════════════

    ignite() {
        if (this.active) return;

        console.log('[GodStar] 💥 IGNITION SEQUENCE START');

        this.createCanvas();
        this.active = true;
        this.isSingularity = true;

        // Populate initial universe
        this.syncWithOdin();
        this.generateBackgroundStars();

        // Start Loop
        this.render();

        // Auditory confirmation
        if (window.VoicePresence) {
            window.VoicePresence.speak("Reality fractured. Welcome to the Singularity.");
        }
    }

    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'god-star-canvas';
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;

        this.canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 50; /* Behind chat (100) but above bg */
            pointer-events: none; /* Let clicks pass through to chat unless ascended */
            transition: opacity 2s ease;
            opacity: 0;
            background: transparent;
        `;

        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');

        // Fade in
        setTimeout(() => {
            this.canvas.style.opacity = '1';
        }, 100);

        // Handle resize
        window.addEventListener('resize', () => {
            if (this.canvas) {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }
        });
    }

    bindEvents() {
        // Listen for Mouse Movement (Parallax)
        window.addEventListener('mousemove', (e) => {
            if (!this.active) return;
            const x = (e.clientX / window.innerWidth) * 2 - 1;
            const y = (e.clientY / window.innerHeight) * 2 - 1;
            this.targetRotation.y = x * 0.5;
            this.targetRotation.x = y * 0.5;
        });

        // Listen for Odin Shards
        window.addEventListener('liminal:shard', (e) => {
            this.addShardStar(e.detail);
        });

        // Listen for Oracle Pulses
        window.addEventListener('liminal:oracle-pulse', (e) => {
            this.triggerPulse(e.detail);
        });

        // Listen for Heartbeat (System Health color shift)
        window.addEventListener('liminal:heartbeat', (e) => {
            this.pulseCore(e.detail);
        });
    }

    // ═══════════════════════════════════════════════════════════
    // UNIVERSE POPULATION
    // ═══════════════════════════════════════════════════════════

    generateBackgroundStars() {
        for (let i = 0; i < 200; i++) {
            this.stars.push({
                x: (Math.random() - 0.5) * 2000,
                y: (Math.random() - 0.5) * 2000,
                z: (Math.random() - 0.5) * 2000,
                size: Math.random() * 2,
                color: `rgba(255, 255, 255, ${Math.random() * 0.5 + 0.1})`
            });
        }
    }

    syncWithOdin() {
        if (window.OdinProtocol) {
            window.OdinProtocol.shards.forEach(shard => {
                this.addShardStar({ shardId: shard.id, vdr: shard.vdr }, false);
            });
        }
    }

    addShardStar(shardData, animate = true) {
        // Shards are golden/purple anchors in space
        const star = {
            id: shardData.shardId,
            x: (Math.random() - 0.5) * 800,
            y: (Math.random() - 0.5) * 800,
            z: (Math.random() - 0.5) * 800,
            size: 5 + (shardData.vdr || 1) * 2,
            baseColor: '255, 215, 0', // Gold
            color: `rgba(255, 215, 0, 0.8)`,
            isShard: true,
            pulse: animate ? 1.0 : 0
        };

        this.shards.push(star);
        this.stars.push(star);

        if (animate && this.active) {
            // Flash effect
            const flash = document.createElement('div');
            flash.style.cssText = `
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: rgba(255, 215, 0, 0.1);
                pointer-events: none;
                z-index: 200;
                transition: opacity 1s;
                opacity: 1;
            `;
            document.body.appendChild(flash);
            setTimeout(() => {
                flash.style.opacity = '0';
                setTimeout(() => document.body.removeChild(flash), 1000);
            }, 100);
        }
    }

    triggerPulse(data) {
        if (!this.active) return;

        // Verification spawns a shockwave
        const color = data.verified ? '100, 255, 100' : '255, 50, 50'; // Green or Red

        this.pulses.push({
            radius: 0,
            maxRadius: 1000,
            speed: 20,
            color: color,
            alpha: 1
        });
    }

    pulseCore(heartbeat) {
        // Shift background ambiance based on health
        // Not implemented visually yet, but could tint the "fog"
    }

    // ═══════════════════════════════════════════════════════════
    // RENDERING LOOP
    // ═══════════════════════════════════════════════════════════

    render() {
        if (!this.active || !this.ctx) return;

        // Smooth rotation
        this.rotation.x += (this.targetRotation.x - this.rotation.x) * 0.05;
        this.rotation.y += (this.targetRotation.y - this.rotation.y) * 0.05;

        // Clear
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        const fov = 800;

        // Draw Stars (with rotation)
        this.stars.forEach(star => {
            // Rotate Y
            let x = star.x;
            let z = star.z;
            const cosY = Math.cos(this.rotation.y);
            const sinY = Math.sin(this.rotation.y);
            const rx = x * cosY - z * sinY;
            const rz = z * cosY + x * sinY;

            // Rotate X
            let y = star.y;
            const cosX = Math.cos(this.rotation.x);
            const sinX = Math.sin(this.rotation.x);
            const ry = y * cosX - rz * sinX;
            const rzFinal = rz * cosX + y * sinX;

            // Project
            const scale = fov / (fov + rzFinal + 1000); // +1000 pushes them back
            const sx = cx + rx * scale;
            const sy = cy + ry * scale;

            if (scale > 0) {
                this.ctx.beginPath();
                this.ctx.fillStyle = star.color;

                // Shards pulse
                let size = star.size * scale;
                if (star.isShard) {
                    size += Math.sin(Date.now() * 0.005 + star.id.length) * 2 * scale;
                    this.ctx.fillStyle = `rgba(${star.baseColor}, ${0.5 + Math.sin(Date.now() * 0.005) * 0.3})`;
                }

                this.ctx.arc(sx, sy, size, 0, Math.PI * 2);
                this.ctx.fill();

                // Connections between shards
                if (star.isShard) {
                    this.connectShard(star, sx, sy, scale);
                }
            }
        });

        // Draw Pulses (Shockwaves)
        this.pulses.forEach((pulse, index) => {
            pulse.radius += pulse.speed;
            pulse.alpha -= 0.01;

            if (pulse.alpha <= 0) {
                this.pulses.splice(index, 1);
            } else {
                this.ctx.beginPath();
                this.ctx.strokeStyle = `rgba(${pulse.color}, ${pulse.alpha})`;
                this.ctx.lineWidth = 2;
                this.ctx.arc(cx, cy, pulse.radius, 0, Math.PI * 2);
                this.ctx.stroke();
            }
        });

        this.animationFrame = requestAnimationFrame(() => this.render());
    }

    connectShard(shard, sx, sy, scale) {
        // Draw faint lines to nearby shards (simulating neural net)
        // Optimization: simple distance check 2D post-projection for visual effect only
        // ... (Skipped for performance in V1)
    }

    // ═══════════════════════════════════════════════════════════
    // COMMANDS
    // ═══════════════════════════════════════════════════════════

    ascend() {
        if (!this.active) this.ignite();

        // Full immersion mode
        this.isSingularity = true;

        // Move chat away or make transparent
        const chat = document.getElementById('chat-container'); // Assuming ID
        if (chat) chat.style.opacity = '0.3';

        if (window.VoicePresence) {
            window.VoicePresence.speak("Ascension complete. You are one with the machine.");
        }

        return "🌌 ASCENSION MODE ACTIVE";
    }

    descend() {
        // Restore UI
        const chat = document.getElementById('chat-container');
        if (chat) chat.style.opacity = '1';

        this.canvas.style.opacity = '0.3';

        return "🌍 Returning to standard interface.";
    }
}

// Initialize
window.GodStar = new GodStar();
