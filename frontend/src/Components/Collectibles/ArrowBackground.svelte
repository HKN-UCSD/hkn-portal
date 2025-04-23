<script>
    import { onMount } from 'svelte';

    // Canvas setup
    let canvas;
    let ctx;

    // Animation constants
    const ARROW_COUNT = 15;
    const ARROW_COLOR = 'rgba(176, 16, 48, 0.7)'; // Crimson with 70% opacity
    
    class Arrow {
        constructor(canvasWidth, canvasHeight) {
            // Initialize position randomly within canvas bounds
            this.x = Math.random() * canvasWidth;
            this.y = Math.random() * canvasHeight;
            
            // Arrow properties
            this.size = Math.random() * 10 + 15;
            this.angle = Math.random() * Math.PI * 2;
            
            // Movement properties
            this.speed = Math.random() * 2 + 1;
            this.velocity = {
                x: Math.cos(this.angle) * this.speed,
                y: Math.sin(this.angle) * this.speed
            };
        }

        update(width, height) {
            // Update position
            this.x += this.velocity.x;
            this.y += this.velocity.y;

            // Handle wall collisions
            if (this.x < 0 || this.x > width) {
                this.velocity.x *= -1;
                this.angle = Math.atan2(this.velocity.y, this.velocity.x);
            }
            if (this.y < 0 || this.y > height) {
                this.velocity.y *= -1;
                this.angle = Math.atan2(this.velocity.y, this.velocity.x);
            }
        }

        draw(ctx) {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle);
            
            // Draw arrow shape
            ctx.beginPath();
            ctx.moveTo(-this.size, -this.size/3);
            ctx.lineTo(0, 0);
            ctx.lineTo(-this.size, this.size/3);
            ctx.lineTo(-this.size * 0.7, 0);
            ctx.closePath();
            
            ctx.fillStyle = ARROW_COLOR;
            ctx.fill();
            
            ctx.restore();
        }
    }

    // Animation state
    const arrows = [];

    function animate() {
        if (!canvas || !ctx) return;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update and draw all arrows
        arrows.forEach(arrow => {
            arrow.update(canvas.width, canvas.height);
            arrow.draw(ctx);
        });
        
        requestAnimationFrame(animate);
    }

    function handleResize() {
        if (!canvas) return;
        
        // Update canvas dimensions
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    onMount(() => {
        if (!canvas) return;
        
        // Initialize canvas context
        ctx = canvas.getContext('2d');
        handleResize();
        
        // Create arrows
        for (let i = 0; i < ARROW_COUNT; i++) {
            arrows.push(new Arrow(canvas.width, canvas.height));
        }
        
        // Start animation loop
        animate();
        
        // Setup resize handler
        window.addEventListener('resize', handleResize);
        
        // Cleanup
        return () => window.removeEventListener('resize', handleResize);
    });
</script>

<div class="fixed inset-0 bg-gray-50">
    <canvas
        bind:this={canvas}
        class="absolute inset-0 w-full h-full opacity-30"
    />
</div> 