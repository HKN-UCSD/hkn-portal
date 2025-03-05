<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";
    import Cookies from "js-cookie"
    import EventsGrid from "../Components/Events/EventsGrid.svelte"
    import { eventGraphics } from "../Components/Events/EventGraphics";
    import EventCreateModal from "../Components/Events/EventCreateModal.svelte"
    let userData;
    let searchQuery = "";  // Stores search input
    let currentDate = new Date().toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    let filters = {
    types: {
        technical: true,
        professional: true,
        outreach: true,
        social: true,
        mentorship: true,
        general: true
    },
    when: {
        upcoming: true,
        past: false
    }
    };

    const savedFilters = Cookies.get("eventFilters");
    if (savedFilters) {
        filters = JSON.parse(savedFilters);
        console.log("onmount filters:", filters)
    }


    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
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
            pk: event.pk,
            location: event.location,
            url: `/events/${event.pk}`,
            type: event.event_type,
            start_time: event.start_time,
            end_time: event.end_time,
            embed_code: event.embed_code ? event.embed_code : eventGraphics[event.event_type],
            is_draft: event.is_draft
        }));

        allEvents.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

        applyFilters();
    }

    function applyFilters() {
        filteredEvents = allEvents
            .filter(event =>
                (filters.when.upcoming && event.end_time > new Date().toISOString()) ||
                (filters.when.past && event.start_time <= new Date().toISOString())
            )
            .filter(event =>
                filters.types[event.type.toLowerCase()] || false
            )
            .filter(event =>
                event.title.toLowerCase().includes(searchQuery.toLowerCase()) || event.description.toLowerCase().includes(searchQuery.toLowerCase())
            )
           ;
            console.log("Applied Filters",filters);
            saveFiltersToCookies();
    }
    function saveFiltersToCookies() {
        Cookies.set("eventFilters", JSON.stringify(filters), { expires: 7, path: '' });
        console.log("Event Filters Cookie:", Cookies.get("eventFilters"));
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


    onMount(() => {
        fetchEvents();
    });


    let isModalOpen = false;

    function openModal() {
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
    }
</script>

<Layout>
    <div class="flex flex-col mt-10">
        <div class="flex flex-col md:flex-row mt-5 overflow-auto gap-7">
            <!-- Sidebar -->
            <div class="md:w-1/4 mb-5">
                <div class="bg-gray-50 active:bg-gray-100 border border-gray-300 rounded-xl shadow-md p-6">
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
            {#await getPermissions()}
                <p>Loading...</p>
            {:then permissions}
                {#if permissions.is_admin}
                    <button
                        class="mt-4 w-full py-4 bg-secondary text-white font-semibold py-2 rounded-lg transition-all duration-300 transform hover:bg-primary"
                        on:click={openModal}>
                    Create Event
                    </button>
                    <EventCreateModal isOpen={isModalOpen} on:close={closeModal} />
                {/if}
            {:catch error}
                <p>Error: {error.message}</p>
            {/await}

            </div>


            <!-- Main Content -->
            <div class="md:w-3/4 bg-gray rounded-lg shadow-md">
                <EventsGrid title="Events" subtitle={currentDate} events={filteredEvents} />
            </div>
        </div>
    </div>
</Layout>
