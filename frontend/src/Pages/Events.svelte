<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";
    import EventsCard from "../Components/Events/EventsCard.svelte";
    import EventBox from "../Components/Events/EventBox.svelte";
    import EventsGrid from "../Components/Events/EventsGrid.svelte"
    let userData;
    let searchQuery = "";  // Stores search input
    let filters = {
    types: {
        technical: true,
        professional: true,
        outreach: true,
        social: true
    },
    when: {
        upcoming: true,
        past: false
    }
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
                (filters.when.upcoming && event.start_time > new Date().toISOString()) ||
                (filters.when.past && event.start_time <= new Date().toISOString())
            )
            .filter(event => 
                filters.types[event.type.toLowerCase()] || false
            )
            .filter(event => 
                event.title.toLowerCase().includes(searchQuery.toLowerCase()) || event.description.toLowerCase().includes(searchQuery.toLowerCase())
            )
           ;
            console.log("Filters",filters)
    }

    // Watch for changes to searchQuery and apply filters dynamically
    $: searchQuery, applyFilters();

    // Select All filters

    function selectAllTypes() {
        Object.keys(filters.types).forEach(type => {
            filters.types[type] = true;
        });
        applyFilters();

    }

    function deselectAllTypes() {
        Object.keys(filters.types).forEach(type => {
            filters.types[type] = false;
        });
        applyFilters();
        console.log("Filters",filters)
    }

    function selectAllWhen() {
        Object.keys(filters.when).forEach(time => {
            filters.when[time] = true;
        });
        applyFilters();
    }

    function deselectAllWhen() {
        Object.keys(filters.when).forEach(time => {
            filters.when[time] = false;
        });
        applyFilters();
    }

     function deselectAllFilters() {
        Object.keys(filters).forEach(key => {
            filters[key] = false;
        });
        applyFilters();
    }


    function selectAllFilters() {
        Object.keys(filters).forEach(category => {
            Object.keys(filters[category]).forEach(key => {
            filters[category][key] = true;
            });
        });
        applyFilters();
        console.log(filters)
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
                    class="w-full p-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    on:input={applyFilters}/>
                    <hr class="my-4 border-gray-300">

                    <div class="flex justify-between items-center mt-4">
                        <h3 class="font-semibold">Type</h3>
                        <div class="flex gap-2 text-[10px]">
                            <button class="text-gray-400 hover:underline cursor-pointer" on:click={selectAllTypes}>Select All</button>
                            <p class = "text-gray-400">|</p>
                            <button class="text-gray-400 hover:underline cursor-pointer" on:click={deselectAllTypes}>Deselect All</button>
                        </div>
                    </div>

                    <div class="space-y-2">
                        {#each Object.keys(filters.types) as type}
                            <label class="flex items-center">
                                <input type="checkbox" bind:checked={filters.types[type]} class="mr-2" on:change={applyFilters}>
                                {type.charAt(0).toUpperCase() + type.slice(1)}
                            </label>
                        {/each}
                    </div>

                    <hr class="my-4 border-gray-300">

                    <div class="flex justify-between items-center mt-4">
                        <h3 class="font-semibold">When</h3>
                        <div class="flex gap-2 text-[10px]">
                            <button class="text-gray-400 hover:underline cursor-pointer" on:click={selectAllWhen}>Select All</button>
                            <p class = "text-gray-400">|</p>
                            <button class="text-gray-400 hover:underline cursor-pointer" on:click={deselectAllWhen}>Deselect All</button>
                        </div>
                    </div>
                    <div class="space-y-2">
                        {#each ['upcoming', 'past'] as time}
                            <label class="flex items-center">
                                <input type="checkbox" bind:checked={filters.when[time]} class="mr-2" on:change={applyFilters}>
                                {time.charAt(0).toUpperCase() + time.slice(1)} Events
                            </label>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="md:w-3/4 bg-white p-6 rounded-lg shadow-md">
                <EventsGrid title="Events" subtitle={null} events={filteredEvents} />
            </div>
        </div>
    </div>
</Layout>
