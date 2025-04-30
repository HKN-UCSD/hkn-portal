<script>
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";
    import CollectibleCard from "../../Components/Collectibles/CollectibleCard.svelte";
    import FilterBar from "../../Components/Collectibles/FilterBar.svelte";
    import EmptyState from "../../Components/Collectibles/EmptyState.svelte";

    // State variables
    let allItems = [];
    let filteredItems = [];
    let isLoading = true;
    let hasError = false;
    let selectedItem = null;
    let showItemDetails = false;

    // Filter state
    let filters = {
        type: 'all',
        rarity: 'all',
        sort: 'name'
    };

    // Fetch all collectibles from the API
    async function fetchCollectibles() {
        isLoading = true;
        hasError = false;
        
        try {
            const response = await fetch('/api/collectibles/catalog/');
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            allItems = data;
            applyFilters();
        } catch (error) {
            console.error("Error fetching collectibles catalog:", error);
            hasError = true;
            
            // For demo purposes, create some sample data if API fails
            allItems = createSampleData();
            applyFilters();
        } finally {
            isLoading = false;
        }
    }

    // Apply filters to the items
    function applyFilters() {
        // Start with all items
        let results = [...allItems];
        
        // Apply type filter
        if (filters.type !== 'all') {
            results = results.filter(item => item.type === filters.type);
        }
        
        // Apply rarity filter
        if (filters.rarity !== 'all') {
            results = results.filter(item => item.rarity === filters.rarity);
        }
        
        // Apply sorting
        results.sort((a, b) => {
            switch (filters.sort) {
                case 'name':
                    return a.name.localeCompare(b.name);
                    
                case 'rarity':
                    // Custom sort order for rarities
                    const rarityOrder = { 
                        legendary: 0, 
                        epic: 1, 
                        rare: 2, 
                        common: 3 
                    };
                    return rarityOrder[a.rarity] - rarityOrder[b.rarity];
                    
                case 'type':
                    return a.type.localeCompare(b.type);
                    
                default:
                    return 0;
            }
        });
        
        filteredItems = results;
    }

    // Handler for filter changes
    function handleFilterChange() {
        applyFilters();
    }
    
    // Handler for item click
    function handleItemClick(item) {
        selectedItem = item;
        showItemDetails = true;
    }
    
    // Close item details modal
    function closeItemDetails() {
        showItemDetails = false;
        setTimeout(() => {
            selectedItem = null;
        }, 300);
    }

    // Create sample data for development/demo
    function createSampleData() {
        const types = ['icon', 'frame', 'banner', 'badge', 'theme'];
        const rarities = ['common', 'rare', 'epic', 'legendary'];
        
        return Array(20).fill().map((_, i) => ({
            id: i + 1,
            name: `Sample Item ${i + 1}`,
            description: `This is a sample ${types[i % types.length]} item for demonstration purposes.`,
            image_url: `/static/placeholder_${rarities[i % rarities.length]}.png`,
            rarity: rarities[i % rarities.length],
            type: types[i % types.length]
        }));
    }

    // Fetch data on component mount
    onMount(async () => {
        await fetchCollectibles();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-crimson-600 mb-4">Engineering Catalog</h1>
            <p class="text-gray-600">Discover all available engineering collectibles</p>
        </div>

        <!-- Loading State -->
        {#if isLoading}
            <div class="flex flex-col items-center justify-center py-20">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-crimson-600 mb-4"></div>
                <p class="text-gray-600">Loading collectibles...</p>
            </div>
        {:else if hasError}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-8 rounded-xl text-center">
                <h3 class="text-xl font-semibold mb-2">Error Loading Data</h3>
                <p>There was a problem loading the collectibles catalog. Please try again later.</p>
                <button 
                    class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    on:click={fetchCollectibles}>
                    Try Again
                </button>
            </div>
        {:else}
            <!-- Filters -->
            <FilterBar 
                bind:filters={filters} 
                on:filter={handleFilterChange} 
            />

            <!-- Catalog Grid -->
            {#if filteredItems.length > 0}
                <div 
                    class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
                    transition:fade={{duration: 200}}
                >
                    {#each filteredItems as item (item.id)}
                        <div transition:fade={{duration: 200}}>
                            <CollectibleCard 
                                {item}
                                onClick={handleItemClick}
                            />
                        </div>
                    {/each}
                </div>
            {:else}
                <EmptyState 
                    message="No matching collectibles found" 
                    subtext="Try adjusting your filters to see more items."
                    icon="✨"
                />
            {/if}
        {/if}

        <!-- Item Details Modal -->
        {#if showItemDetails && selectedItem}
            <div 
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
                on:click={closeItemDetails}
                on:keydown={(e) => e.key === 'Escape' && closeItemDetails()}
                transition:fade={{duration: 200}}
                role="dialog"
                aria-modal="true"
                tabindex="-1"
            >
                <div 
                    class="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden"
                    on:click|stopPropagation
                    on:keydown={(e) => e.key === 'Enter' && e.stopPropagation()}
                    role="button"
                    tabindex="0"
                >
                    <!-- Modal Header -->
                    <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                        <h3 class="text-lg font-semibold text-gray-900">{selectedItem.name}</h3>
                        <button 
                            class="text-gray-500 hover:text-gray-700 focus:outline-none"
                            on:click={closeItemDetails}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Modal Body -->
                    <div class="p-6">
                        <div class="flex flex-col items-center mb-4">
                            <div class="w-32 h-32 bg-gray-50 rounded-lg overflow-hidden border border-gray-200 mb-4">
                                <img 
                                    src={selectedItem.image_url} 
                                    alt={selectedItem.name} 
                                    class="w-full h-full object-contain p-2"
                                />
                            </div>
                            
                            <div class="flex space-x-2 mb-4">
                                <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full capitalize">{selectedItem.type}</span>
                                <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full capitalize">{selectedItem.rarity}</span>
                            </div>
                        </div>
                        
                        {#if selectedItem.description}
                            <div class="mb-4">
                                <h4 class="text-sm font-medium text-gray-700 mb-2">Description</h4>
                                <p class="text-gray-600 text-sm">{selectedItem.description}</p>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        {/if}
    </div>
</CollectiblesLayout> 