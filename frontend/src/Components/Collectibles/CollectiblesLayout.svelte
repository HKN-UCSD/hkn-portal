<script>
    import { Link } from "svelte-routing";
    import { adminStatus } from "../../stores.js";
    import ArrowBackground from "../../Components/Collectibles/ArrowBackground.svelte";

    let logo = "/static/HKN-Logo-New-Blue.png";
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
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100">
                        Home
                    </Link>
                    <Link 
                        to="/collectibles/blueprint" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100">
                        Blueprint
                    </Link>
                    <Link 
                        to="/collectibles/inventory" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100">
                        Inventory
                    </Link>
                    <Link 
                        to="/collectibles/loadout" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100">
                        Loadout
                    </Link>
                    <Link 
                        to="/collectibles/catalog" 
                        class="relative px-4 py-2 text-sm md:text-lg font-medium transition-all duration-300 text-white/90 hover:text-white after:block after:h-0.5 after:w-full after:bg-white/70 after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100">
                        Catalog
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