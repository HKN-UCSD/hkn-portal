<script>
    import { Link, navigate } from "svelte-routing";
    import { onMount } from 'svelte';
    import { adminStatus } from "../../stores.js";
    import ArrowBackground from "../../Components/Collectibles/ArrowBackground.svelte";

    let logo = "/static/HKN-Logo-New-Blue.png";

    // Check if user is on the current page
    let currentPath = "";

    onMount(() => {
        currentPath = window.location.pathname;
    });

    // Function to check if a link is active
    function isActive(path) {
        return currentPath === path;
    }
</script>

<div class="min-h-screen relative">
    <ArrowBackground />
    
    <!-- Collectibles Navigation Bar -->
    <nav class="bg-gradient-to-b from-crimson-600 to-crimson-700/90 text-white sticky top-0 w-full z-50 shadow-lg backdrop-blur-sm border-b border-white/10">
        <div class="container mx-auto px-4">
            <div class="flex h-16 justify-between">
                <!-- Logo -->
                <a href="/" class="flex items-center hover:bg-white/10 px-4 py-2 rounded-xl transition-all duration-300 ease-in-out">
                    <img class="h-10 w-auto object-contain filter brightness-0 invert" src={logo} alt="HKN Logo" />
                </a>

                <!-- Navigation Links -->
                <div class="flex items-center space-x-6">
                    <Link 
                        to="/collectibles/gachahome" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100 {isActive('/collectibles/gachahome') ? 'bg-crimson-50 text-crimson-600' : ''}"
                    >
                        Home
                    </Link>
                    <Link 
                        to="/collectibles/blueprint" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100 {isActive('/collectibles/blueprint') ? 'bg-crimson-50 text-crimson-600' : ''}"
                    >
                        Blueprint
                    </Link>
                    <Link 
                        to="/collectibles/loadout" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100 {isActive('/collectibles/loadout') ? 'bg-crimson-50 text-crimson-600' : ''}"
                    >
                        Loadout
                    </Link>
                    <Link 
                        to="/collectibles/catalog" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100 {isActive('/collectibles/catalog') ? 'bg-crimson-50 text-crimson-600' : ''}"
                    >
                        Catalog
                    </Link>
                    <Link 
                        to="/collectibles/upload" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100 {isActive('/collectibles/upload') ? 'bg-crimson-50 text-crimson-600' : ''}"
                    >
                        Upload
                    </Link>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main class="container mx-auto relative z-10">
        <slot />
    </main>
</div> 