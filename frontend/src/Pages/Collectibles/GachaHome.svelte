<script>
    import { onMount } from "svelte";
    import Layout from "../../Layout.svelte";
    import { navigate } from "svelte-routing";
    import CollectiblesLayout from "../../Components/Collectibles/CollectiblesLayout.svelte";

    let eventsAttended = 0;
    let availableDrafts = 0;
    let featuredCollectibles = [];
    let recentAcquisitions = [];
    let nextDraftProgress = 0;

    async function fetchCollectibleData() {
        try {
            const response = await fetch('/api/collectibles/');
            const data = await response.json();
            eventsAttended = data.events_attended;
            availableDrafts = Math.floor(eventsAttended / 3);
            featuredCollectibles = data.featured;
            recentAcquisitions = data.recent;
            nextDraftProgress = (eventsAttended % 3) * 33.33;
        } catch (error) {
            console.error("Error fetching collectible data:", error);
        }
    }

    onMount(async () => {
        await fetchCollectibleData();
    });
</script>

<CollectiblesLayout>
    <div class="container mx-auto px-4 py-8">
        <!-- Header Section -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-primary mb-4">Gacha Collectibles</h1>
            <p class="text-gray-600">Design, collect, and showcase your engineering achievements</p>
        </div>

        <!-- Progress Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-xl shadow-md">
                <h3 class="text-lg font-semibold mb-2">Events Attended</h3>
                <p class="text-3xl font-bold text-primary">{eventsAttended}</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-md">
                <h3 class="text-lg font-semibold mb-2">Available Drafts</h3>
                <p class="text-3xl font-bold text-primary">{availableDrafts}</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-md">
                <h3 class="text-lg font-semibold mb-2">Next Draft Progress</h3>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-primary h-2.5 rounded-full" style="width: {nextDraftProgress}%"></div>
                </div>
                <p class="text-sm text-gray-600 mt-2">{nextDraftProgress}% to next draft</p>
            </div>
        </div>

        <!-- Featured Collectibles -->
        <div class="mb-8">
            <h2 class="text-2xl font-bold mb-4">Featured Items</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {#each featuredCollectibles as item}
                    <div class="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow">
                        <img src={item.image_url} alt={item.name} class="w-full h-48 object-cover rounded-lg mb-4"/>
                        <h3 class="text-lg font-semibold">{item.name}</h3>
                        <p class="text-gray-600">{item.description}</p>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Recent Acquisitions -->
        <div>
            <h2 class="text-2xl font-bold mb-4">Recent Acquisitions</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                {#each recentAcquisitions as item}
                    <div class="bg-white p-4 rounded-xl shadow-md">
                        <img src={item.image_url} alt={item.name} class="w-full h-32 object-cover rounded-lg mb-2"/>
                        <h3 class="text-sm font-semibold">{item.name}</h3>
                    </div>
                {/each}
            </div>
        </div>
    </div>
</CollectiblesLayout> 