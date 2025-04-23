<script>
    import { onMount } from "svelte";
    import Layout from "../../Layout.svelte";
    import { fade } from "svelte/transition";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";

    let allItems = [];
    let filters = {
        type: 'all',
        rarity: 'all',
        season: 'all',
        sort: 'name'
    };
    let seasons = ['all', 'spring', 'summer', 'fall', 'winter'];

    async function fetchCatalog() {
        try {
            const response = await fetch('/api/collectibles/catalog/');
            allItems = await response.json();
        } catch (error) {
            console.error("Error fetching catalog:", error);
        }
    }

    function getFilteredItems() {
        let filtered = [...allItems];
        
        // Apply filters
        if (filters.type !== 'all') {
            filtered = filtered.filter(item => item.type === filters.type);
        }
        if (filters.rarity !== 'all') {
            filtered = filtered.filter(item => item.rarity === filters.rarity);
        }
        if (filters.season !== 'all') {
            filtered = filtered.filter(item => item.season === filters.season);
        }

        // Apply sorting
        switch (filters.sort) {
            case 'name':
                filtered.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'rarity':
                const rarityOrder = { legendary: 0, epic: 1, rare: 2, common: 3 };
                filtered.sort((a, b) => rarityOrder[a.rarity] - rarityOrder[b.rarity]);
                break;
            case 'type':
                filtered.sort((a, b) => a.type.localeCompare(b.type));
                break;
        }

        return filtered;
    }

    onMount(async () => {
        await fetchCatalog();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-primary mb-4">Engineering Catalog</h1>
            <p class="text-gray-600">Discover all available engineering collectibles</p>
        </div>

        <!-- Filters -->
        <div class="bg-white p-6 rounded-xl shadow-lg mb-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <select 
                    class="p-2 border rounded-lg"
                    bind:value={filters.type}>
                    <option value="all">All Types</option>
                    <option value="icon">Profile Icons</option>
                    <option value="frame">Avatar Frames</option>
                    <option value="banner">Profile Banners</option>
                    <option value="badge">Badges</option>
                    <option value="theme">UI Themes</option>
                </select>

                <select 
                    class="p-2 border rounded-lg"
                    bind:value={filters.rarity}>
                    <option value="all">All Rarities</option>
                    <option value="common">Common</option>
                    <option value="rare">Rare</option>
                    <option value="epic">Epic</option>
                    <option value="legendary">Legendary</option>
                </select>

                <select 
                    class="p-2 border rounded-lg"
                    bind:value={filters.season}>
                    {#each seasons as season}
                        <option value={season} class="capitalize">
                            {season === 'all' ? 'All Seasons' : season}
                        </option>
                    {/each}
                </select>

                <select 
                    class="p-2 border rounded-lg"
                    bind:value={filters.sort}>
                    <option value="name">Sort by Name</option>
                    <option value="rarity">Sort by Rarity</option>
                    <option value="type">Sort by Type</option>
                </select>
            </div>
        </div>

        <!-- Catalog Grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {#each getFilteredItems() as item}
                <div class="bg-white p-4 rounded-xl shadow-md">
                    <div class="relative">
                        <img 
                            src={item.image_url} 
                            alt={item.name} 
                            class="w-full aspect-square object-cover rounded-lg mb-4"/>
                        {#if item.is_seasonal}
                            <div class="absolute top-2 right-2 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs">
                                Seasonal
                            </div>
                        {/if}
                    </div>
                    <h3 class="font-semibold mb-1">{item.name}</h3>
                    <div class="flex justify-between items-center text-sm">
                        <span class="text-gray-600 capitalize">{item.type}</span>
                        <span class="font-medium capitalize" class:text-blue-500={item.rarity === 'rare'} 
                                                      class:text-purple-500={item.rarity === 'epic'}
                                                      class:text-yellow-500={item.rarity === 'legendary'}>
                            {item.rarity}
                        </span>
                    </div>
                    {#if item.season}
                        <div class="mt-2 text-xs text-gray-500 capitalize">
                            Season: {item.season}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    </div>
</CollectiblesLayout> 