<script>
    import { createEventDispatcher } from 'svelte';

    // Props
    export let filters = {
        type: 'all',
        rarity: 'all',
        sort: 'name'
    };

    // Type options
    export let typeOptions = [
        { value: 'all', label: 'All Types' },
        { value: 'icon', label: 'Profile Icons' },
        { value: 'frame', label: 'Avatar Frames' },
        { value: 'banner', label: 'Profile Banners' },
        { value: 'badge', label: 'Badges' },
        { value: 'theme', label: 'UI Themes' }
    ];

    // Rarity options
    export let rarityOptions = [
        { value: 'all', label: 'All Rarities' },
        { value: 'common', label: 'Common' },
        { value: 'rare', label: 'Rare' },
        { value: 'epic', label: 'Epic' },
        { value: 'legendary', label: 'Legendary' }
    ];

    // Sort options
    export let sortOptions = [
        { value: 'name', label: 'Sort by Name' },
        { value: 'rarity', label: 'Sort by Rarity' },
        { value: 'type', label: 'Sort by Type' }
    ];

    const dispatch = createEventDispatcher();

    // Handle filter changes
    function handleFilterChange() {
        dispatch('filter', filters);
    }
</script>

<div class="bg-white p-4 rounded-xl shadow-md mb-6 border border-gray-200">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Type Filter -->
        <div class="relative">
            <label for="typeFilter" class="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select 
                id="typeFilter"
                class="block w-full rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-sm focus:border-crimson-500 focus:outline-none focus:ring-1 focus:ring-crimson-500"
                bind:value={filters.type}
                on:change={handleFilterChange}>
                {#each typeOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        </div>

        <!-- Rarity Filter -->
        <div class="relative">
            <label for="rarityFilter" class="block text-sm font-medium text-gray-700 mb-1">Rarity</label>
            <select 
                id="rarityFilter"
                class="block w-full rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-sm focus:border-crimson-500 focus:outline-none focus:ring-1 focus:ring-crimson-500"
                bind:value={filters.rarity}
                on:change={handleFilterChange}>
                {#each rarityOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        </div>

        <!-- Sort Order -->
        <div class="relative">
            <label for="sortFilter" class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select 
                id="sortFilter"
                class="block w-full rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-sm focus:border-crimson-500 focus:outline-none focus:ring-1 focus:ring-crimson-500"
                bind:value={filters.sort}
                on:change={handleFilterChange}>
                {#each sortOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        </div>
    </div>
</div> 