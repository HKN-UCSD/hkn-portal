<script>
    export let item = {};
    export let compact = false;
    export let onClick = null;

    // Rarity color mapping for borders and accents
    const rarityColors = {
        common: {
            border: "border-gray-400",
            bg: "bg-gray-50",
            text: "text-gray-700",
            glow: "shadow-gray-200"
        },
        rare: {
            border: "border-blue-400",
            bg: "bg-blue-50",
            text: "text-blue-600",
            glow: "shadow-blue-200"
        },
        epic: {
            border: "border-purple-400",
            bg: "bg-purple-50",
            text: "text-purple-600",
            glow: "shadow-purple-200"
        },
        legendary: {
            border: "border-amber-400",
            bg: "bg-amber-50",
            text: "text-amber-600",
            glow: "shadow-amber-200"
        }
    };

    // Type icons
    const typeIcons = {
        icon: "👤",
        frame: "🖼️",
        banner: "🏳️",
        badge: "🏅",
        theme: "🎨"
    };

    // Get the color scheme based on rarity
    $: colorScheme = rarityColors[item.rarity] || rarityColors.common;
    
    // Handle click events
    function handleClick() {
        if (onClick) onClick(item);
    }
</script>

<!-- Card Component -->
<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
<div 
    class="relative rounded-lg overflow-hidden transition-all duration-300 bg-white hover:shadow-lg {compact ? 'h-full' : ''}"
    class:cursor-pointer={onClick}
    class:transform={onClick}
    class:hover:scale-102={onClick}
    class:border-2={!compact}
    class:{colorScheme.border}={!compact}
    class:shadow-md={!compact}
    class:hover:shadow-lg={!compact}
    on:click={handleClick}
    on:keydown={(e) => e.key === 'Enter' && handleClick()}
    role={onClick ? "button" : "article"}
    tabindex={onClick ? "0" : null}
>
    <!-- Image Container -->
    <div class="relative">
        <!-- Item Image -->
        <div class="{compact ? 'h-16 w-16' : 'aspect-square w-full'} overflow-hidden {colorScheme.bg}">
            <img 
                src={item.image_url} 
                alt={item.name} 
                class="w-full h-full object-contain p-2"
            />
        </div>
        
        <!-- Rarity Badge -->
        {#if !compact}
            <div class="absolute top-2 right-2 {colorScheme.bg} {colorScheme.text} px-2 py-1 text-xs font-semibold rounded-full border {colorScheme.border} capitalize">
                {item.rarity}
            </div>
        {/if}

        <!-- Type Icon -->
        <div class="absolute bottom-2 left-2 w-6 h-6 flex items-center justify-center rounded-full bg-white/80 backdrop-blur-sm border {colorScheme.border} {colorScheme.text} text-xs">
            {typeIcons[item.type] || "?"}
        </div>
    </div>

    <!-- Card Content -->
    {#if !compact}
        <div class="p-3 h-24">
            <!-- Item Name -->
            <h3 class="font-semibold text-gray-800 mb-1 truncate">{item.name}</h3>
            
            <!-- Item Metadata -->
            <div class="flex justify-between items-center">
                <span class="text-xs text-gray-500 capitalize">{item.type}</span>
                <span class="text-xs font-medium {colorScheme.text} capitalize">{item.rarity}</span>
            </div>
            
            <!-- Truncated Description -->
            {#if item.description}
                <div class="w-3/4 mt-2 overflow-hidden">
                    <p class="text-xs text-gray-600 whitespace-nowrap overflow-hidden text-ellipsis">{item.description}</p>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    /* Custom scale for hover effect */
    .hover\:scale-102:hover {
        transform: scale(1.02);
    }
</style> 