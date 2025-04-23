<script>
    import { onMount } from "svelte";
    import { fade, fly, draw } from "svelte/transition";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";
    import BlueprintDrawing from "../../Components/Collectibles/BlueprintDrawing.svelte";

    let availableDrafts = 1;
    let isDrafting = false;
    let draftResult = null;
    let recentDrafts = [];
    let draftingStage = 0;
    let blueprintScale = 1;
    let draftError = null;

    const rarityProbabilities = {
        common: { chance: 60, color: 'bg-gray-500' },
        rare: { chance: 25, color: 'bg-blue-500' },
        epic: { chance: 10, color: 'bg-purple-500' },
        legendary: { chance: 5, color: 'bg-yellow-500' }
    };

    const draftingStages = [
        { text: "Initializing Circuit Design", duration: 2000 },
        { text: "Routing Circuit Traces", duration: 2000 },
        { text: "Finalizing Blueprint", duration: 2000 }
    ];

    async function fetchDraftData() {
        try {
            const response = await fetch('/api/collectibles/drafts/');
            const data = await response.json();
            availableDrafts = Math.max(1, data.available_drafts);
            recentDrafts = data.recent_drafts || [];
        } catch (error) {
            console.error("Error fetching draft data:", error);
            availableDrafts = 1;
        }
    }

    async function startDraft() {
        if (availableDrafts <= 0 || isDrafting) return;
        
        try {
            isDrafting = true;
            draftResult = null;
            draftError = null;
            
            // Start the drafting animation sequence
            for (let i = 0; i < draftingStages.length; i++) {
                draftingStage = i + 1;
                await new Promise(resolve => setTimeout(resolve, draftingStages[i].duration));
            }

            try {
                const response = await fetch('/api/collectibles/draft/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }
                
                const result = await response.json();
                draftResult = result;
                availableDrafts--;
                recentDrafts = [result, ...recentDrafts.slice(0, 4)];
            } catch (error) {
                console.error("Error performing draft:", error);
                draftError = "Failed to complete draft. Please try again.";
            }
        } catch (error) {
            console.error("Draft process error:", error);
            draftError = "An unexpected error occurred.";
        } finally {
            // Ensure we always reset the drafting state
            setTimeout(() => {
                isDrafting = false;
                draftingStage = 0;
            }, 500); // Small delay for animation to finish
        }
    }

    onMount(async () => {
        await fetchDraftData();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-crimson-600 mb-4">Engineering Blueprint</h1>
            <p class="text-gray-600">Design circuit boards and collect engineering artifacts</p>
        </div>

        <!-- Main Content -->
        <div class="max-w-3xl mx-auto">
            <!-- Available Drafts Counter -->
            <div class="text-center mb-6">
                <div class="inline-block px-6 py-2 rounded-full bg-crimson-600 text-white font-bold mb-4">
                    Available Drafts: {availableDrafts}
                </div>
            </div>

            <!-- Blueprint Drafting Area -->
            <div class="relative h-[600px] mb-4 bg-blue-50/50 rounded-lg border-2 border-blue-200 overflow-hidden">
                <!-- Blueprint Grid Background -->
                <div class="absolute inset-0" style="background-image: linear-gradient(#2195f318 1px, transparent 1px), linear-gradient(90deg, #2195f318 1px, transparent 1px); background-size: 20px 20px;">
                </div>

                <!-- Blueprint Drawing Animation -->
                <BlueprintDrawing isDrawing={isDrafting} />

                <!-- Drafting Content -->
                <div class="relative h-full flex items-center justify-center">
                    {#if isDrafting}
                        <div class="text-center" transition:fade>
                            <div class="text-lg font-semibold text-crimson-600">
                                {draftingStages[draftingStage - 1]?.text || 'Initializing...'}
                            </div>
                        </div>
                    {:else if draftError}
                        <div class="text-center text-red-500" transition:fade>
                            <p>{draftError}</p>
                            <button 
                                class="mt-4 px-4 py-2 bg-crimson-600 text-white rounded-lg hover:bg-crimson-700"
                                on:click={() => draftError = null}>
                                Dismiss
                            </button>
                        </div>
                    {:else if draftResult}
                        <div class="text-center" transition:fade>
                            <img src={draftResult.image_url} 
                                 alt={draftResult.name} 
                                 class="w-48 h-48 mx-auto mb-4 object-contain filter drop-shadow-lg"
                                 style="transform: scale({blueprintScale})"
                                 on:mouseenter={() => blueprintScale = 1.1}
                                 on:mouseleave={() => blueprintScale = 1}
                                 transition:fade/>
                            <h3 class="text-2xl font-bold text-crimson-600">{draftResult.name}</h3>
                            <p class="text-lg text-gray-600 capitalize">{draftResult.rarity}</p>
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Draft Button -->
            <div class="text-center mb-8">
                <button 
                    class="bg-crimson-600 text-white px-8 py-4 rounded-lg hover:bg-crimson-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 font-bold text-lg shadow-lg"
                    on:click={startDraft}
                    disabled={isDrafting || availableDrafts <= 0}>
                    Start Circuit Draft
                </button>
            </div>

            <!-- Rarity Probabilities -->
            <div class="grid grid-cols-4 gap-4 mb-8">
                {#each Object.entries(rarityProbabilities) as [rarity, { chance, color }]}
                    <div class="text-center p-3 rounded-lg bg-white shadow-sm border border-gray-100">
                        <div class="text-sm font-semibold capitalize mb-1">{rarity}</div>
                        <div class="flex items-center justify-center space-x-2">
                            <div class={`w-3 h-3 rounded-full ${color}`}></div>
                            <div class="text-lg font-bold text-gray-700">{chance}%</div>
                        </div>
                    </div>
                {/each}
            </div>

            <!-- Recent Drafts -->
            <div>
                <h2 class="text-xl font-bold mb-4 text-crimson-600">Recent Blueprints</h2>
                <div class="space-y-4">
                    {#each recentDrafts as draft, i}
                        <div class="bg-white/80 backdrop-blur-sm p-4 rounded-lg shadow-md border border-gray-200"
                             transition:fly={{y: 20, duration: 300, delay: i * 100}}>
                            <div class="flex items-center space-x-4">
                                <img src={draft.image_url} 
                                     alt={draft.name} 
                                     class="w-16 h-16 rounded-lg object-contain"/>
                                <div>
                                    <h3 class="font-semibold text-crimson-600">{draft.name}</h3>
                                    <p class="text-sm text-gray-600 capitalize">{draft.rarity}</p>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</CollectiblesLayout>

<style>
    /* Smooth transitions for blueprint scale */
    img {
        transition: transform 0.3s ease-in-out;
    }
</style> 