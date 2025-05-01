<script>
    import { onMount } from "svelte";
    import { fade } from "svelte/transition";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";
    import CollectibleCard from "../../Components/Collectibles/CollectibleCard.svelte";
    import FilterBar from "../../Components/Collectibles/FilterBar.svelte";
    import EmptyState from "../../Components/Collectibles/EmptyState.svelte";

    // User profile data
    let userData = null;

    // Profile loadout state
    let originalEquippedItems = {
        icon: null,
        frame: null,
        banner: null,
        badge: null,
        theme: null
    };

    let equippedItems = {
        icon: null,
        frame: null,
        banner: null,
        badge: null,
        theme: null
    };
    
    // Track whether changes have been made
    let hasUnsavedChanges = false;
    let isSaving = false;
    let saveSuccess = false;
    let saveError = null;
    
    // Inventory state
    let inventory = [];
    let filteredItems = [];
    let isLoading = true;
    let hasError = false;
    let selectedItem = null;
    let showItemDetails = false;
    
    // Drag and drop state
    let isDragging = false;
    let draggedItem = null;
    let activeSlot = null;

    // Filter state
    let filters = {
        type: 'all',
        rarity: 'all',
        sort: 'name'
    };

    // Filter options
    const typeOptions = [
        { value: 'all', label: 'All Types' },
        { value: 'icon', label: 'Profile Icons' },
        { value: 'frame', label: 'Avatar Frames' },
        { value: 'banner', label: 'Profile Banners' },
        { value: 'badge', label: 'Badges' },
        { value: 'theme', label: 'UI Themes' }
    ];

    // Fetch user profile data
    async function fetchUserProfile() {
        try {
            const response = await fetch('/api/profile/self/');
            if (!response.ok) {
                throw new Error(`Profile API error: ${response.status}`);
            }
            userData = await response.json();
        } catch (error) {
            console.error("Error fetching user profile:", error);
        }
    }

    // Fetch all inventory and loadout data
    async function fetchUserItems() {
        isLoading = true;
        hasError = false;
        
        try {
            const response = await fetch('/api/collectibles/loadout/');
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Store the original equipped items
            originalEquippedItems = JSON.parse(JSON.stringify(data.equipped || {
                icon: null,
                frame: null,
                banner: null,
                badge: null,
                theme: null
            }));
            
            // Set current equipped items
            equippedItems = JSON.parse(JSON.stringify(originalEquippedItems));
            
            inventory = data.available || [];
            
            // Reset unsaved changes flag
            hasUnsavedChanges = false;
            saveSuccess = false;
            saveError = null;
            
            applyFilters();
        } catch (error) {
            console.error("Error fetching loadout data:", error);
            hasError = true;
        } finally {
            isLoading = false;
        }
    }

    // Apply filters to inventory items
    function applyFilters() {
        // Start with all inventory items
        let results = [...inventory];
        
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

    // Check if the profile has been modified
    function checkForChanges() {
        // Compare current equipped items with original equipped items
        for (const slot in equippedItems) {
            const current = equippedItems[slot];
            const original = originalEquippedItems[slot];
            
            // If one is null and the other isn't, there's a change
            if ((current === null && original !== null) || 
                (current !== null && original === null)) {
                return true;
            }
            
            // If both are not null, compare IDs
            if (current !== null && original !== null) {
                if (current.id !== original.id) {
                    return true;
                }
            }
        }
        
        return false;
    }

    // Handle filter changes
    function handleFilterChange() {
        applyFilters();
    }

    // Open item details modal
    function openItemDetails(item) {
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

    // Handle drag and drop for equipping items
    function handleDragStart(item) {
        isDragging = true;
        draggedItem = item;
    }

    function handleDragEnd() {
        isDragging = false;
        draggedItem = null;
        activeSlot = null;
    }

    function handleDragEnter(slot) {
        if (draggedItem && draggedItem.type === slot) {
            activeSlot = slot;
        }
    }

    function handleDragLeave() {
        activeSlot = null;
    }

    function handleDrop(slot) {
        if (!draggedItem || draggedItem.type !== slot) return;
        
        // Update equipped items in the profile preview
        equippedItems[slot] = draggedItem;
        
        // Update item equipped status in inventory (visual only, not saved to DB yet)
        inventory = inventory.map(item => {
            // First unequip any currently equipped item of this type in our local state
            if (item.type === slot && item.is_equipped) {
                return {...item, is_equipped: false};
            }
            // Then equip the dragged item in our local state
            if (item.id === draggedItem.id) {
                return {...item, is_equipped: true};
            }
            return item;
        });
        
        // Check if this change should be tracked
        hasUnsavedChanges = checkForChanges();
        
        // Reapply filters to update the UI
        applyFilters();
        
        handleDragEnd();
    }

    // Handle equip/unequip from modal (local state only)
    function toggleEquip(item) {
        // If equipping, determine which slot to use
        const slot = item.type;
        const shouldEquip = !item.is_equipped;
        
        if (shouldEquip) {
            // Update equipped items in the profile preview
            equippedItems[slot] = item;
            
            // Update item equipped status in inventory
            inventory = inventory.map(invItem => {
                // First unequip any currently equipped item of this type
                if (invItem.type === slot && invItem.is_equipped) {
                    return {...invItem, is_equipped: false};
                }
                // Then equip the selected item
                if (invItem.id === item.id) {
                    return {...invItem, is_equipped: true};
                }
                return invItem;
            });
        } else {
            // Remove from equipped items
            equippedItems[slot] = null;
            
            // Update item equipped status in inventory
            inventory = inventory.map(invItem => 
                invItem.id === item.id ? {...invItem, is_equipped: false} : invItem
            );
        }
        
        // Update selected item
        if (selectedItem) {
            selectedItem = {...selectedItem, is_equipped: shouldEquip};
        }
        
        // Check if this change should be tracked
        hasUnsavedChanges = checkForChanges();
        
        // Reapply filters
        applyFilters();
    }
    
    // Save changes to the database
    async function saveChanges() {
        isSaving = true;
        saveError = null;
        
        try {
            // Create a list of equip/unequip operations needed
            const operations = [];
            
            // Process each slot
            for (const slot in equippedItems) {
                const current = equippedItems[slot];
                const original = originalEquippedItems[slot];
                
                // If current is null but original had something, we need to unequip
                if (current === null && original !== null) {
                    operations.push({
                        id: original.id,
                        slot: null,
                        equip: false
                    });
                }
                // If current has something but different from original, we need to equip
                else if (current !== null && (original === null || current.id !== original.id)) {
                    operations.push({
                        id: current.id,
                        slot: slot,
                        equip: true
                    });
                }
            }
            
            // Execute each operation sequentially
            for (const op of operations) {
                const response = await fetch(`/api/collectibles/${op.id}/equip/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                        slot: op.slot,
                        equip: op.equip
                })
            });
            
                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }
            }
            
            // If we get here, all operations succeeded
            // Update the original equipped items to match current state
            originalEquippedItems = JSON.parse(JSON.stringify(equippedItems));
            hasUnsavedChanges = false;
            saveSuccess = true;
            
            // Clear success message after 3 seconds
            setTimeout(() => {
                saveSuccess = false;
            }, 3000);
        } catch (error) {
            console.error("Error saving loadout changes:", error);
            saveError = "Failed to save changes. Please try again.";
        } finally {
            isSaving = false;
        }
    }

    onMount(async () => {
        await Promise.all([fetchUserProfile(), fetchUserItems()]);
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-crimson-600 mb-4">Your Engineering Profile</h1>
            <p class="text-gray-600">Customize your engineering appearance and manage your collectibles</p>
        </div>

        <!-- Loading State -->
        {#if isLoading}
            <div class="flex flex-col items-center justify-center py-20">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-crimson-600 mb-4"></div>
                <p class="text-gray-600">Loading your collection...</p>
            </div>
        {:else if hasError}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-8 rounded-xl text-center">
                <h3 class="text-xl font-semibold mb-2">Error Loading Data</h3>
                <p>There was a problem loading your collectibles. Please try again later.</p>
                <button 
                    class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    on:click={fetchUserItems}>
                    Try Again
                </button>
            </div>
        {:else}
            <!-- Main Content -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Profile Preview -->
                <div class="lg:col-span-1">
                    <div class="bg-white p-6 rounded-xl shadow-lg sticky top-20">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-xl font-bold text-crimson-600">Profile Preview</h2>
                            
                            {#if hasUnsavedChanges}
                                <button 
                                    class="px-4 py-2 bg-crimson-600 text-white rounded-lg text-sm font-medium hover:bg-crimson-700 transition-colors flex items-center disabled:opacity-50"
                                    on:click={saveChanges}
                                    disabled={isSaving}>
                                    {#if isSaving}
                                        <div class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                                        Saving...
                                    {:else}
                                        Save Changes
                                    {/if}
                                </button>
                            {/if}
                        </div>
                        
                        {#if saveSuccess}
                            <div class="bg-green-50 text-green-700 p-2 rounded-lg mb-4 text-sm text-center">
                                Profile saved successfully!
                            </div>
                        {/if}
                        
                        {#if saveError}
                            <div class="bg-red-50 text-red-700 p-2 rounded-lg mb-4 text-sm text-center">
                                {saveError}
                            </div>
                        {/if}
                        
                <div class="relative">
                            <!-- Banner Drop Zone -->
                    <div 
                                class="h-32 bg-gray-100 rounded-t-xl transition-all duration-200 {activeSlot === 'banner' ? 'bg-blue-100 border-2 border-blue-300' : ''}"
                        on:dragover|preventDefault
                                on:dragenter={() => handleDragEnter('banner')}
                                on:dragleave={handleDragLeave}
                        on:drop={() => handleDrop('banner')}>
                        {#if equippedItems.banner}
                            <img 
                                src={equippedItems.banner.image_url} 
                                alt="Banner" 
                                class="w-full h-full object-cover rounded-t-xl"/>
                        {/if}
                    </div>
                    
                            <!-- Profile Picture with Frame Drop Zone -->
                    <div class="relative -mt-16 flex justify-center">
                                <!-- Frame Drop Zone -->
                        <div 
                                    class="relative rounded-full {activeSlot === 'frame' ? 'bg-blue-100 border-2 border-blue-300' : ''}"
                            on:dragover|preventDefault
                                    on:dragenter={() => handleDragEnter('frame')}
                                    on:dragleave={handleDragLeave}
                            on:drop={() => handleDrop('frame')}>
                            {#if equippedItems.frame}
                                <img 
                                    src={equippedItems.frame.image_url} 
                                    alt="Frame" 
                                    class="absolute inset-0 w-32 h-32"/>
                            {/if}
                                    
                                    <!-- Icon Drop Zone (with actual profile picture if available) -->
                                    <div 
                                        class="w-32 h-32 bg-gray-200 rounded-full overflow-hidden border-4 border-white {activeSlot === 'icon' ? 'bg-blue-100 border-blue-300' : ''}"
                                        on:dragover|preventDefault
                                        on:dragenter={() => handleDragEnter('icon')}
                                        on:dragleave={handleDragLeave}
                                        on:drop={() => handleDrop('icon')}>
                            {#if equippedItems.icon}
                                <img 
                                    src={equippedItems.icon.image_url} 
                                    alt="Profile Icon" 
                                                class="w-full h-full object-cover"/>
                                        {:else if userData && userData.profile_picture}
                                            <img 
                                                src={userData.profile_picture} 
                                                alt="Profile Picture" 
                                                class="w-full h-full object-cover"/>
                            {/if}
                                    </div>
                        </div>
                    </div>

                            <!-- Badge Drop Zone -->
                    <div 
                                class="absolute top-4 right-4 w-12 h-12 flex items-center justify-center rounded-lg {activeSlot === 'badge' ? 'bg-blue-100 border-2 border-blue-300' : ''}"
                        on:dragover|preventDefault
                                on:dragenter={() => handleDragEnter('badge')}
                                on:dragleave={handleDragLeave}
                        on:drop={() => handleDrop('badge')}>
                        {#if equippedItems.badge}
                            <img 
                                src={equippedItems.badge.image_url} 
                                alt="Badge" 
                                        class="w-full h-full object-contain"/>
                                {/if}
                            </div>
                        </div>

                        <div class="mt-20 text-center">
                            <h3 class="font-semibold text-gray-900">{userData ? userData.preferred_name : 'Your'} Engineering Profile</h3>
                            <p class="text-sm text-gray-600 mt-2">Drag and drop items to customize your appearance</p>
                            {#if hasUnsavedChanges}
                                <p class="text-xs text-amber-600 mt-1">You have unsaved changes</p>
                            {/if}
                        </div>
                    </div>
                </div>

                <!-- Collection Management -->
                <div class="lg:col-span-2">
                    <div class="bg-white p-6 rounded-xl shadow-lg">
                        <h2 class="text-xl font-bold mb-4 text-crimson-600">Your Collection</h2>
                        
                        <!-- Filters -->
                        <FilterBar 
                            bind:filters={filters}
                            typeOptions={typeOptions}
                            on:filter={handleFilterChange} 
                        />

                        <!-- Collection Grid -->
                        {#if filteredItems.length > 0}
                            <div 
                                class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-4"
                                transition:fade={{duration: 200}}
                            >
                                {#each filteredItems as item (item.id)}
                                    <div 
                                        class="relative" 
                                        draggable="true"
                                        on:dragstart={() => handleDragStart(item)}
                                        on:dragend={handleDragEnd}
                                        on:click={() => openItemDetails(item)}
                                        transition:fade={{duration: 200}}
                                    >
                                        <CollectibleCard {item} />
                                        {#if item.is_equipped}
                                            <div class="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium z-10">
                                                Equipped
                                            </div>
                                        {/if}
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
                    </div>
                </div>
            </div>
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
                            <div class="w-40 h-40 bg-gray-50 rounded-lg overflow-hidden border border-gray-200 mb-4">
                            <img 
                                    src={selectedItem.image_url} 
                                    alt={selectedItem.name} 
                                    class="w-full h-full object-contain p-2"
                                />
                            </div>
                            
                            <div class="flex space-x-2 mb-4">
                                <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full capitalize">{selectedItem.type}</span>
                                <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full capitalize">{selectedItem.rarity}</span>
                                {#if selectedItem.is_equipped}
                                    <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Equipped</span>
                                {/if}
                            </div>
                        </div>
                        
                        {#if selectedItem.description}
                            <div class="mb-4">
                                <h4 class="text-sm font-medium text-gray-700 mb-2">Description</h4>
                                <p class="text-gray-600 text-sm">{selectedItem.description}</p>
                            </div>
                        {/if}

                        <button 
                            class="w-full mt-4 bg-crimson-600 text-white px-4 py-2 rounded-lg hover:bg-crimson-700 transition-colors"
                            on:click={() => toggleEquip(selectedItem)}>
                            {selectedItem.is_equipped ? 'Unequip' : `Equip as ${selectedItem.type}`}
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    </div>
</CollectiblesLayout> 