<script>
    import { onMount } from "svelte";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";
    import { fade } from "svelte/transition";

    let inventory = [];
    let selectedItem = null;
    let showItemDetails = false;
    let filters = {
        type: 'all',
        rarity: 'all'
    };

    async function fetchInventory() {
        try {
            const response = await fetch('/api/collectibles/inventory/');
            inventory = await response.json();
        } catch (error) {
            console.error("Error fetching inventory:", error);
        }
    }

    function openItemDetails(item) {
        selectedItem = item;
        showItemDetails = true;
    }

    async function toggleEquip(item) {
        try {
            const response = await fetch(`/api/collectibles/${item.id}/equip/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    equip: !item.is_equipped
                })
            });
            if (response.ok) {
                item.is_equipped = !item.is_equipped;
                // Update the inventory list
                inventory = inventory.map(i => 
                    i.id === item.id ? {...i, is_equipped: !i.is_equipped} : i
                );
            }
        } catch (error) {
            console.error("Error toggling equip status:", error);
        }
    }

    function closeItemDetails() {
        showItemDetails = false;
        selectedItem = null;
    }

    onMount(async () => {
        await fetchInventory();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-primary mb-4">Engineering Collection</h1>
            <p class="text-gray-600">Manage your collection of engineering achievements</p>
        </div>

        <!-- Filters -->
        <div class="bg-white p-4 rounded-xl shadow-md mb-6">
            <div class="flex flex-wrap gap-4">
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
            </div>
        </div>

        <!-- Inventory Grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {#each inventory.filter(item => 
                (filters.type === 'all' || item.type === filters.type) &&
                (filters.rarity === 'all' || item.rarity === filters.rarity)
            ) as item}
                <div 
                    class="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                    on:click={() => openItemDetails(item)}
                    on:keydown={(e) => e.key === 'Enter' && openItemDetails(item)}
                    role="button"
                    tabindex="0">
                    <div class="relative">
                        <img 
                            src={item.image_url} 
                            alt={item.name} 
                            class="w-full aspect-square object-cover rounded-lg mb-2"/>
                        {#if item.is_equipped}
                            <div class="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs">
                                Equipped
                            </div>
                        {/if}
                    </div>
                    <h3 class="font-semibold truncate">{item.name}</h3>
                    <p class="text-sm text-gray-600 capitalize">{item.rarity}</p>
                </div>
            {/each}
        </div>

        <!-- Item Details Modal -->
        {#if showItemDetails}
            <div 
                class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
                on:click={closeItemDetails}
                on:keydown={(e) => e.key === 'Escape' && closeItemDetails()}
                role="button"
                tabindex="0">
                <div 
                    class="bg-white p-6 rounded-xl shadow-lg max-w-md w-full mx-4"
                    on:click|stopPropagation
                    on:keydown={(e) => e.key === 'Enter' && e.stopPropagation()}
                    role="button"
                    tabindex="0">
                    <div class="flex justify-between items-start mb-4">
                        <h2 class="text-2xl font-bold">{selectedItem.name}</h2>
                        <button 
                            class="text-gray-500 hover:text-gray-700"
                            on:click={closeItemDetails}>
                            ✕
                        </button>
                    </div>
                    <img 
                        src={selectedItem.image_url} 
                        alt={selectedItem.name} 
                        class="w-full aspect-square object-cover rounded-lg mb-4"/>
                    <p class="text-gray-600 mb-4">{selectedItem.description}</p>
                    <div class="flex justify-between items-center">
                        <div>
                            <span class="text-sm text-gray-500">Type:</span>
                            <span class="ml-2 capitalize">{selectedItem.type}</span>
                        </div>
                        <div>
                            <span class="text-sm text-gray-500">Rarity:</span>
                            <span class="ml-2 capitalize">{selectedItem.rarity}</span>
                        </div>
                    </div>
                    <button 
                        class="w-full mt-4 bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors"
                        on:click={() => toggleEquip(selectedItem)}>
                        {selectedItem.is_equipped ? 'Unequip' : 'Equip'}
                    </button>
                </div>
            </div>
        {/if}
    </div>
</CollectiblesLayout>