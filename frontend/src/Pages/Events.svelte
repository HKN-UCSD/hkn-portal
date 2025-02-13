<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";
    import EventsCard from "../Components/EventsCard.svelte";

    let userData;
    let searchQuery = "";  // Stores search input
    let filters = {
        technical: false,
        professional: true,
        outreach: false,
        social: false,
        upcoming: true,
        past: false
    };

    let allEvents = [];
    let filteredEvents = [];

    async function getUserData() {
        try {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
                userData = await response.json();
            } else {
                console.error("Failed to fetch self data");
            }
        } catch (error) {
            console.error("Error fetching user data", error);
        }
    }

    async function fetchEvents() {
        await getUserData();
        const res = await getEvents();
        const curr = new Date().toISOString();

        allEvents = res.map(event => ({
            title: event.name,
            description: event.description,
            id: event.pk,
            url: `/events/${event.pk}`,
            type: event.event_type,
            start_time: event.start_time
        }));

        applyFilters();
    }

    function applyFilters() {
        filteredEvents = allEvents
            .filter(event => 
                (filters.upcoming && event.start_time > new Date().toISOString()) ||
                (filters.past && event.start_time <= new Date().toISOString())
            )
            .filter(event => 
                filters[event.type.toLowerCase()] || false
            )
            .filter(event => 
                event.title.toLowerCase().includes(searchQuery.toLowerCase())
            );
    }

    // Watch for changes to searchQuery and apply filters dynamically
    $: searchQuery, applyFilters();

    // Select All filters
    function selectAllFilters() {
        Object.keys(filters).forEach(key => {
            filters[key] = true;
        });
        applyFilters();
    }

    // Deselect All filters
    function deselectAllFilters() {
        Object.keys(filters).forEach(key => {
            filters[key] = false;
        });
        applyFilters();
    }

    onMount(fetchEvents);
</script>

<Layout>
    <div class="flex flex-col mt-10">
        <div class="flex flex-col md:flex-row mt-5 overflow-auto gap-7">
            <!-- Sidebar -->
            <div class="md:w-1/4 mb-5">
                <div class="bg-white p-5 rounded-lg shadow-md">
                    <h2 class="text-xl font-semibold mb-4">Filter</h2>
                    <!-- Search Bar -->
                    <input 
                    type="text" 
                    bind:value={searchQuery} 
                    placeholder="Search events..." 
                    class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    on:input={applyFilters}/>
                    <hr class="my-4 border-gray-300">

                    <h3 class="mt-4 font-semibold">Type</h3>
                    <div class="space-y-2">
                        <button class="w-full bg-gray-200 p-2 rounded-md" on:click={selectAllFilters}>Select All</button>
                        <button class="w-full bg-gray-200 p-2 rounded-md mt-2" on:click={deselectAllFilters}>Deselect All</button>

                        {#each Object.keys(filters).slice(0, 4) as type}
                            <label class="flex items-center">
                                <input type="checkbox" bind:checked={filters[type]} class="mr-2" on:change={applyFilters}>
                                {type.charAt(0).toUpperCase() + type.slice(1)}
                            </label>
                        {/each}
                    </div>

                    <hr class="my-4 border-gray-300">
                    <h3 class="mt-4 font-semibold">When</h3>
                    <div class="space-y-2">
                        {#each ['upcoming', 'past'] as time}
                            <label class="flex items-center">
                                <input type="checkbox" bind:checked={filters[time]} class="mr-2" on:change={applyFilters}>
                                {time.charAt(0).toUpperCase() + time.slice(1)} Events
                            </label>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="md:w-3/4 bg-white p-6 rounded-lg shadow-md">
                <EventsCard title="Events" subtitle={null} events={filteredEvents} />
            </div>
        </div>
    </div>
</Layout>
