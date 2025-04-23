<script>
    import { onMount } from "svelte";
    import Layout from "../../Layout.svelte";
    import { fade } from "svelte/transition";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";

    let equippedItems = {
        icon: null,
        frame: null,
        banner: null,
        badge: null,
        theme: null
    };
    let availableItems = [];
    let isDragging = false;
    let draggedItem = null;

    async function fetchLoadoutData() {
        try {
            const response = await fetch('/api/collectibles/loadout/');
            const data = await response.json();
            equippedItems = data.equipped;
            availableItems = data.available;
        } catch (error) {
            console.error("Error fetching loadout data:", error);
        }
    }

    function handleDragStart(item) {
        isDragging = true;
        draggedItem = item;
    }

    function handleDragEnd() {
        isDragging = false;
        draggedItem = null;
    }

    async function handleDrop(slot) {
        if (!draggedItem) return;
        
        try {
            const response = await fetch(`/api/collectibles/${draggedItem.id}/equip/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    slot: slot,
                    equip: true
                })
            });
            
            if (response.ok) {
                // Update equipped items
                equippedItems[slot] = draggedItem;
                // Update available items
                availableItems = availableItems.map(item => 
                    item.id === draggedItem.id ? {...item, is_equipped: true} : item
                );
            }
        } catch (error) {
            console.error("Error equipping item:", error);
        }
    }

    onMount(async () => {
        await fetchLoadoutData();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-primary mb-4">Engineering Loadout</h1>
            <p class="text-gray-600">Customize your engineering profile appearance</p>
        </div>

        <!-- Loadout Preview -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Profile Preview -->
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <h2 class="text-xl font-bold mb-4">Profile Preview</h2>
                <div class="relative">
                    <!-- Banner -->
                    <div 
                        class="h-32 bg-gray-100 rounded-t-xl"
                        on:dragover|preventDefault
                        on:drop={() => handleDrop('banner')}>
                        {#if equippedItems.banner}
                            <img 
                                src={equippedItems.banner.image_url} 
                                alt="Banner" 
                                class="w-full h-full object-cover rounded-t-xl"/>
                        {/if}
                    </div>
                    
                    <!-- Profile Picture with Frame -->
                    <div class="relative -mt-16 flex justify-center">
                        <div 
                            class="relative"
                            on:dragover|preventDefault
                            on:drop={() => handleDrop('frame')}>
                            {#if equippedItems.frame}
                                <img 
                                    src={equippedItems.frame.image_url} 
                                    alt="Frame" 
                                    class="absolute inset-0 w-32 h-32"/>
                            {/if}
                            {#if equippedItems.icon}
                                <img 
                                    src={equippedItems.icon.image_url} 
                                    alt="Profile Icon" 
                                    class="w-32 h-32 rounded-full border-4 border-white"/>
                            {/if}
                        </div>
                    </div>

                    <!-- Badge -->
                    <div 
                        class="absolute top-4 right-4"
                        on:dragover|preventDefault
                        on:drop={() => handleDrop('badge')}>
                        {#if equippedItems.badge}
                            <img 
                                src={equippedItems.badge.image_url} 
                                alt="Badge" 
                                class="w-12 h-12"/>
                        {/if}
                    </div>
                </div>
            </div>

            <!-- Available Items -->
            <div>
                <h2 class="text-xl font-bold mb-4">Available Items</h2>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {#each availableItems as item}
                        <div 
                            class="bg-white p-4 rounded-xl shadow-md cursor-move"
                            draggable="true"
                            on:dragstart={() => handleDragStart(item)}
                            on:dragend={handleDragEnd}>
                            <img 
                                src={item.image_url} 
                                alt={item.name} 
                                class="w-full aspect-square object-cover rounded-lg mb-2"/>
                            <h3 class="font-semibold truncate">{item.name}</h3>
                            <p class="text-sm text-gray-600 capitalize">{item.type}</p>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</CollectiblesLayout> 