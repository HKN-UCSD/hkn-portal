<script>
    import { onMount, onDestroy } from "svelte";
    export let isDrawing = false;
    
    let animationProgress = 0;
    let animationFrame = null;
    let pathsProgress = Array(8).fill(0);
    let isAnimating = false;
    
    // Circuit board path definitions
    const circuitPaths = [
        "M50,150 Q80,80 150,120 T250,80 L300,100 Q320,130 350,150", // Main horizontal path
        "M100,50 Q120,100 100,150 T120,200 L100,250", // Vertical connection 1
        "M150,120 L150,200 Q170,220 200,220", // Vertical connection 2
        "M250,80 L250,180 Q230,200 200,220", // Vertical connection 3
        "M300,100 L300,150 Q320,180 300,200 L300,250", // Vertical connection 4
        "M50,150 L20,150 Q10,180 20,200 L50,200", // Left component
        "M350,150 L380,150 Q390,180 380,200 L350,200", // Right component
        "M200,220 L200,270 Q170,290 150,270 L120,250" // Bottom component
    ];
    
    // Circuit node positions for connection points
    const circuitNodes = [
        {x: 50, y: 150, r: 3}, // Left node
        {x: 150, y: 120, r: 3}, // Top left junction
        {x: 250, y: 80, r: 3}, // Top right junction
        {x: 300, y: 100, r: 3}, // Right junction
        {x: 350, y: 150, r: 3}, // Right node
        {x: 100, y: 150, r: 3}, // Left vertical
        {x: 150, y: 200, r: 3}, // Middle top
        {x: 250, y: 180, r: 3}, // Middle bottom
        {x: 300, y: 200, r: 3}, // Right vertical
        {x: 200, y: 220, r: 3}, // Bottom junction
        {x: 100, y: 250, r: 3}, // Bottom left
        {x: 300, y: 250, r: 3}  // Bottom right
    ];

    // Calculate stroke-dashoffset based on progress
    function calculateOffset(progress, totalLength) {
        return totalLength - ((progress || 0) * totalLength / 100);
    }
    
    // Start continuous animation
    function startAnimation() {
        if (!isDrawing || isAnimating) return;
        
        try {
            isAnimating = true;
            let startTime = performance.now();
            let duration = 6000; // 6 seconds for full animation
            
            // Different start delays for each path (in ms)
            const delays = [0, 200, 400, 600, 800, 1000, 1200, 1400];
            
            function animate(currentTime) {
                try {
                    if (!isDrawing || !isAnimating) {
                        cancelAnimationFrame(animationFrame);
                        animationFrame = null;
                        return;
                    }
                    
                    const elapsed = currentTime - startTime;
                    
                    if (elapsed <= duration) {
                        animationProgress = Math.min(100, (elapsed / duration) * 100);
                        
                        // Update each path with its own delay - optimize to prevent too many updates
                        for (let i = 0; i < pathsProgress.length; i++) {
                            if (elapsed <= delays[i]) {
                                pathsProgress[i] = 0;
                            } else {
                                const pathElapsed = elapsed - delays[i];
                                const pathDuration = duration - delays[i];
                                pathsProgress[i] = Math.min(100, (pathElapsed / pathDuration) * 100);
                            }
                        }
                        
                        animationFrame = requestAnimationFrame(animate);
                    } else {
                        animationProgress = 100;
                        pathsProgress = Array(8).fill(100);
                        isAnimating = false;
                    }
                } catch (error) {
                    console.error("Animation frame error:", error);
                    cancelAnimationFrame(animationFrame);
                    animationFrame = null;
                    isAnimating = false;
                }
            }
            
            animationFrame = requestAnimationFrame(animate);
        } catch (error) {
            console.error("Animation start error:", error);
            isAnimating = false;
        }
    }
    
    // Clean up animation properly
    function stopAnimation() {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
            animationFrame = null;
        }
        isAnimating = false;
    }
    
    // React to drawing state changes
    $: {
        if (isDrawing && !isAnimating) {
            animationProgress = 0;
            pathsProgress = Array(8).fill(0);
            // Small delay to ensure the component is fully mounted
            setTimeout(startAnimation, 50);
        } else if (!isDrawing) {
            stopAnimation();
        }
    }
    
    onMount(() => {
        // Ensure animation stops when component mounts
        stopAnimation();
    });
    
    onDestroy(() => {
        // Make sure to clean up on destroy
        stopAnimation();
    });
</script>

{#if isDrawing}
    <svg class="absolute inset-0 w-full h-full" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid meet">
        <!-- Circuit Board Grid Background -->
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1E88E5" stroke-width="0.2" opacity="0.3"/>
        </pattern>
        <rect width="400" height="300" fill="url(#grid)" />
        
        <!-- Circuit Paths -->
        {#each circuitPaths as path, i}
            <path 
                d={path}
                fill="none" 
                stroke="#FF5252" 
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-dasharray="1000"
                style="stroke-dashoffset: {calculateOffset(pathsProgress[i], 1000)};" 
                opacity="0.8"
            />
        {/each}
        
        <!-- Circuit Connection Points (appear as animation progresses) -->
        {#each circuitNodes as node, i}
            {#if animationProgress > i * 8}
                <circle 
                    cx={node.x} 
                    cy={node.y} 
                    r={node.r}
                    fill="#FFD740"
                    opacity={Math.min(1, (animationProgress - (i * 8)) / 10)}
                />
            {/if}
        {/each}
        
        <!-- Component Symbols (appear at the end) -->
        {#if animationProgress > 80}
            <!-- Resistor Symbol -->
            <path 
                d="M70,175 L80,165 L90,185 L100,165 L110,185 L120,165 L130,175"
                fill="none" 
                stroke="#64B5F6" 
                stroke-width="1.5"
                opacity={Math.min(1, (animationProgress - 80) / 20)}
            />
            
            <!-- Capacitor Symbol -->
            <g opacity={Math.min(1, (animationProgress - 85) / 15)}>
                <line x1="260" y1="180" x2="260" y2="160" stroke="#64B5F6" stroke-width="1.5" />
                <line x1="270" y1="180" x2="270" y2="160" stroke="#64B5F6" stroke-width="1.5" />
                <line x1="250" y1="170" x2="260" y2="170" stroke="#64B5F6" stroke-width="1.5" />
                <line x1="270" y1="170" x2="280" y2="170" stroke="#64B5F6" stroke-width="1.5" />
            </g>
            
            <!-- IC Chip Symbol -->
            <g opacity={Math.min(1, (animationProgress - 90) / 10)}>
                <rect x="150" y="140" width="60" height="40" fill="none" stroke="#64B5F6" stroke-width="1.5" rx="2" />
                <line x1="160" y1="140" x2="160" y2="180" stroke="#64B5F6" stroke-width="1" />
                <line x1="170" y1="140" x2="170" y2="180" stroke="#64B5F6" stroke-width="1" />
                <line x1="180" y1="140" x2="180" y2="180" stroke="#64B5F6" stroke-width="1" />
                <line x1="190" y1="140" x2="190" y2="180" stroke="#64B5F6" stroke-width="1" />
                <line x1="200" y1="140" x2="200" y2="180" stroke="#64B5F6" stroke-width="1" />
                <circle cx="155" cy="145" r="2" fill="#64B5F6" />
            </g>
        {/if}
    </svg>
{/if}

<style>
    path, circle, line, rect {
        transition: opacity 0.3s ease-out;
    }
    
    path {
        transition: stroke-dashoffset 0.1s linear;
    }
</style> 