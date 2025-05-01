<script>
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";
    import CollectibleCard from "../../Components/Collectibles/CollectibleCard.svelte";
    import { fade } from "svelte/transition";

    // Active tab
    let activeTab = "upload"; // "upload" or "manage"

    // Form data
    let formData = {
        name: "",
        description: "",
        image_url: "",
        rarity: "common",
        type: "badge",
        is_seasonal: false,
        season: ""
    };

    // Form state
    let isSubmitting = false;
    let submitError = null;
    let submitSuccess = false;
    let isAdmin = false;

    // Management state
    let existingCollectibles = [];
    let filteredCollectibles = [];
    let isLoadingCollectibles = false;
    let loadCollectiblesError = null;
    let selectedCollectible = null;
    let showDeleteConfirmation = false;
    let isDeleting = false;
    let deleteError = null;
    let deleteSuccess = null;
    let searchQuery = "";

    // Options for select inputs
    const rarityOptions = [
        { value: "common", label: "Common" },
        { value: "rare", label: "Rare" },
        { value: "epic", label: "Epic" },
        { value: "legendary", label: "Legendary" }
    ];

    const typeOptions = [
        { value: "icon", label: "Profile Icon" },
        { value: "frame", label: "Avatar Frame" },
        { value: "banner", label: "Profile Banner" },
        { value: "badge", label: "Badge" },
        { value: "theme", label: "UI Theme" }
    ];

    // Get CSRF token from cookie
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        return cookieValue ? cookieValue.split('=')[1] : '';
    }

    // Check if user is admin
    async function checkAdminPermissions() {
        try {
            const response = await fetch('/api/permissions/');
            const data = await response.json();
            isAdmin = data.is_admin || false;
            
            if (!isAdmin) {
                submitError = "You don't have permission to add collectibles. Admin access required.";
            } else {
                // Load collectibles if user is admin
                await loadCollectibles();
            }
        } catch (error) {
            console.error("Error checking permissions:", error);
            submitError = "Error checking permissions. Please try again later.";
        }
    }

    // Load existing collectibles
    async function loadCollectibles() {
        isLoadingCollectibles = true;
        loadCollectiblesError = null;
        
        try {
            const response = await fetch('/api/collectibles/catalog/');
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            // Get the collectibles and ensure they're sorted consistently
            const items = await response.json();
            existingCollectibles = items.sort((a, b) => a.name.localeCompare(b.name));
            filterCollectibles();
        } catch (error) {
            console.error("Error loading collectibles:", error);
            loadCollectiblesError = "Error loading collectibles. Please try again.";
        } finally {
            isLoadingCollectibles = false;
        }
    }

    // Filter collectibles based on search query
    function filterCollectibles() {
        if (!searchQuery.trim()) {
            filteredCollectibles = [...existingCollectibles];
            return;
        }
        
        const query = searchQuery.toLowerCase();
        filteredCollectibles = existingCollectibles.filter(item => 
            item.name.toLowerCase().includes(query) || 
            (item.description && item.description.toLowerCase().includes(query)) ||
            item.type.toLowerCase().includes(query) ||
            item.rarity.toLowerCase().includes(query)
        );
    }

    // Handle form submission for adding a collectible
    async function handleSubmit() {
        if (!isAdmin) {
            submitError = "You don't have permission to add collectibles. Admin access required.";
            return;
        }

        isSubmitting = true;
        submitError = null;
        submitSuccess = false;

        try {
            // Validate form data
            if (!formData.name || !formData.image_url || !formData.type) {
                throw new Error("Name, image URL, and type are required fields");
            }

            // Get CSRF token
            const csrfToken = getCSRFToken();

            // Call the API to add the collectible
            const response = await fetch('/api/collectibles/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData),
                credentials: 'include'  // Include cookies in the request
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Error creating collectible");
            }

            const result = await response.json();
            console.log("Collectible created:", result);
            
            // Reset form and show success message
            formData = {
                name: "",
                description: "",
                image_url: "",
                rarity: "common",
                type: "badge",
                is_seasonal: false,
                season: ""
            };
            
            submitSuccess = true;
            
            // Reload collectibles
            await loadCollectibles();
        } catch (error) {
            console.error("Error submitting form:", error);
            submitError = error.message || "Error creating collectible. Please try again.";
        } finally {
            isSubmitting = false;
        }
    }

    // Show delete confirmation for a collectible
    function showDeleteModal(collectible) {
        selectedCollectible = collectible;
        showDeleteConfirmation = true;
        deleteError = null;
    }

    // Cancel delete
    function cancelDelete() {
        showDeleteConfirmation = false;
        selectedCollectible = null;
        deleteError = null;
    }

    // Confirm and execute delete
    async function confirmDelete() {
        if (!selectedCollectible) return;
        
        isDeleting = true;
        deleteError = null;
        deleteSuccess = null;
        
        try {
            // Get CSRF token
            const csrfToken = getCSRFToken();
            
            // Call API to delete collectible
            const response = await fetch(`/api/collectibles/delete/${selectedCollectible.id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'include'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Error deleting collectible");
            }
            
            const result = await response.json();
            deleteSuccess = result.message || "Collectible deleted successfully";
            
            // Reset state
            showDeleteConfirmation = false;
            
            // Optimistically update local lists before reloading
            existingCollectibles = existingCollectibles.filter(item => item.id !== selectedCollectible.id);
            filterCollectibles();
            
            selectedCollectible = null;
            
            // Reload to ensure consistency with server
            await loadCollectibles();
        } catch (error) {
            console.error("Error deleting collectible:", error);
            deleteError = error.message || "Error deleting collectible. Please try again.";
        } finally {
            isDeleting = false;
        }
    }

    // Initialize component
    onMount(async () => {
        await checkAdminPermissions();
    });

    // Watch for search query changes
    $: if (searchQuery !== undefined) {
        filterCollectibles();
    }
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8 max-w-5xl">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-crimson-600 mb-4">Collectibles Management</h1>
            <p class="text-gray-600">Add, edit, and manage collectibles in the system</p>
        </div>

        <!-- Admin Access Warning -->
        {#if !isAdmin}
            <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-8 rounded-xl text-center mb-8">
                <h3 class="text-xl font-semibold mb-2">Admin Access Required</h3>
                <p>You need administrator privileges to manage collectibles.</p>
            </div>
        {:else}
            <!-- Tab Navigation -->
            <div class="flex border-b border-gray-200 mb-8">
                <button 
                    class="px-4 py-2 font-medium text-sm mr-2 {activeTab === 'upload' ? 'text-crimson-600 border-b-2 border-crimson-500' : 'text-gray-500 hover:text-gray-700'}"
                    on:click={() => activeTab = 'upload'}
                >
                    Upload New Collectible
                </button>
                <button 
                    class="px-4 py-2 font-medium text-sm {activeTab === 'manage' ? 'text-crimson-600 border-b-2 border-crimson-500' : 'text-gray-500 hover:text-gray-700'}"
                    on:click={() => activeTab = 'manage'}
                >
                    Manage Existing Collectibles
                </button>
            </div>

            <!-- Success/Error Messages -->
            {#if deleteSuccess}
                <div class="mb-6 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg">
                    {deleteSuccess}
                </div>
            {/if}

            <!-- Upload Tab Content -->
            {#if activeTab === 'upload'}
                <div class="bg-white shadow-md rounded-xl p-6 mb-8">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Add New Collectible</h2>
                    
                    <form on:submit|preventDefault={handleSubmit}>
                        <!-- Name -->
                        <div class="mb-4">
                            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                            <input 
                                type="text" 
                                id="name" 
                                bind:value={formData.name} 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                                required
                            />
                        </div>

                        <!-- Description -->
                        <div class="mb-4">
                            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                            <textarea 
                                id="description" 
                                bind:value={formData.description} 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500 h-24"
                            ></textarea>
                        </div>

                        <!-- Image URL -->
                        <div class="mb-4">
                            <label for="image_url" class="block text-sm font-medium text-gray-700 mb-1">Image URL *</label>
                            <input 
                                type="url" 
                                id="image_url" 
                                bind:value={formData.image_url} 
                                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                                required
                                placeholder="https://example.com/image.png"
                            />
                            {#if formData.image_url}
                                <div class="mt-2 border border-gray-200 rounded-lg p-2 flex justify-center bg-gray-50">
                                    <img 
                                        src={formData.image_url} 
                                        alt="Collectible preview" 
                                        class="h-24 object-contain"
                                        on:error={(e) => e.target.src = "https://placehold.co/400x400?text=Invalid+Image"}
                                    />
                                </div>
                            {/if}
                        </div>

                        <!-- Type and Rarity (side by side) -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <!-- Type -->
                            <div>
                                <label for="type" class="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                                <select 
                                    id="type" 
                                    bind:value={formData.type} 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                                    required
                                >
                                    {#each typeOptions as option}
                                        <option value={option.value}>{option.label}</option>
                                    {/each}
                                </select>
                            </div>

                            <!-- Rarity -->
                            <div>
                                <label for="rarity" class="block text-sm font-medium text-gray-700 mb-1">Rarity</label>
                                <select 
                                    id="rarity" 
                                    bind:value={formData.rarity} 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                                >
                                    {#each rarityOptions as option}
                                        <option value={option.value}>{option.label}</option>
                                    {/each}
                                </select>
                            </div>
                        </div>

                        <!-- Seasonal Options -->
                        <div class="mb-6">
                            <div class="flex items-center mb-2">
                                <input 
                                    type="checkbox" 
                                    id="is_seasonal" 
                                    bind:checked={formData.is_seasonal} 
                                    class="h-4 w-4 text-crimson-600 focus:ring-crimson-500 border-gray-300 rounded"
                                />
                                <label for="is_seasonal" class="ml-2 block text-sm text-gray-700">Seasonal Item</label>
                            </div>
                            
                            {#if formData.is_seasonal}
                                <div class="pl-6 mt-2">
                                    <label for="season" class="block text-sm font-medium text-gray-700 mb-1">Season Name</label>
                                    <input 
                                        type="text" 
                                        id="season" 
                                        bind:value={formData.season} 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                                        placeholder="e.g. Fall 2023"
                                    />
                                </div>
                            {/if}
                        </div>

                        <!-- Success/Error Messages -->
                        {#if submitSuccess}
                            <div class="mb-6 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg">
                                Collectible created successfully!
                            </div>
                        {/if}

                        {#if submitError}
                            <div class="mb-6 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                                {submitError}
                            </div>
                        {/if}

                        <!-- Submit Button -->
                        <div class="flex justify-end">
                            <button 
                                type="submit"
                                class="px-4 py-2 bg-crimson-600 text-white rounded-lg hover:bg-crimson-700 disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Creating...' : 'Create Collectible'}
                            </button>
                        </div>
                    </form>
                </div>
            {:else}
                <!-- Manage Tab Content -->
                <div class="bg-white shadow-md rounded-xl p-6 mb-8">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Manage Collectibles</h2>
                    
                    <!-- Search Bar -->
                    <div class="mb-6">
                        <div class="relative">
                            <input 
                                type="text" 
                                bind:value={searchQuery}
                                placeholder="Search collectibles..." 
                                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-crimson-500"
                            />
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute left-3 top-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                    </div>
                    
                    <!-- Loading State -->
                    {#if isLoadingCollectibles}
                        <div class="flex justify-center py-8">
                            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-crimson-600"></div>
                        </div>
                    <!-- Error State -->
                    {:else if loadCollectiblesError}
                        <div class="p-4 bg-red-50 text-red-700 rounded-lg text-center">
                            {loadCollectiblesError}
                            <button 
                                class="ml-2 underline"
                                on:click={loadCollectibles}
                            >
                                Try Again
                            </button>
                        </div>
                    <!-- Empty State -->
                    {:else if filteredCollectibles.length === 0}
                        <div class="text-center py-8 text-gray-500">
                            {searchQuery ? 'No collectibles match your search' : 'No collectibles found in the database'}
                        </div>
                    <!-- Collectibles Grid -->
                    {:else}
                        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {#each filteredCollectibles as collectible, index (collectible.id)}
                                <div class="relative group">
                                    <CollectibleCard item={collectible} />
                                    
                                    <!-- Delete Button Overlay -->
                                    <button
                                        class="absolute top-2 right-2 bg-red-600 text-white p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                                        on:click={() => showDeleteModal(collectible)}
                                        title="Delete Collectible"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            {/if}

            <!-- Delete Confirmation Modal -->
            {#if showDeleteConfirmation && selectedCollectible}
                <!-- Modal Backdrop -->
                <div 
                    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                    on:click={cancelDelete}
                    transition:fade={{ duration: 200 }}
                >
                    <!-- Modal Content -->
                    <div 
                        class="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4"
                        on:click|stopPropagation
                    >
                        <h3 class="text-xl font-bold text-gray-800 mb-4">Confirm Deletion</h3>
                        
                        <p class="mb-6 text-gray-600">
                            Are you sure you want to delete the collectible "{selectedCollectible.name}"? This action cannot be undone.
                        </p>
                        
                        {#if deleteError}
                            <div class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
                                {deleteError}
                            </div>
                        {/if}
                        
                        <div class="flex justify-end space-x-3">
                            <button
                                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                                on:click={cancelDelete}
                                disabled={isDeleting}
                            >
                                Cancel
                            </button>
                            <button
                                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                                on:click={confirmDelete}
                                disabled={isDeleting}
                            >
                                {isDeleting ? 'Deleting...' : 'Delete'}
                            </button>
                        </div>
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</CollectiblesLayout> 