<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";
    import EventPopUp from "../Components/EventPopUp.svelte";
    import PointBar from "../Components/PointBar.svelte";
    import EventsCard from "../Components/Events/EventsCard.svelte";
    import { eventGraphics } from "../Components/Events/EventGraphics.js";

    let selectedEvent = null;
    let showPopup = false;

    function handleEventClick(event) {
        selectedEvent = event;
        showPopup = true;  // Show popup when an event card is clicked
    }

    // Function to close the popup
    function closePopup() {
        showPopup = false;
    }

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    };

    let userData;

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

    let events = [];

    onMount(async () => {
        // Fetch events from the server
        await getUserData();
        const res = await getEvents()
        const curr = new Date().toISOString();
        // filter by start time and only show title and description
        events = res
        .filter(event => event.end_time > curr && !event.is_draft) // Exclude drafts
        .map(event => ({
            title: event.name,
            description: event.description,
            start_time: event.start_time,
            end_time: event.end_time,
            location: event.location,
            event_type: event.event_type,
            pk: event.pk,
            url: `/events/${event.pk}`,
            embed_code: event.embed_code ? event.embed_code : eventGraphics[event.event_type],
            is_draft: event.is_draft,
            points: event.points,
            event_type: event.event_type,
        }));

        events.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

        const handleKeydown = (event) => {
        if (event.key === "Escape") {
            closePopup();
        }
        };
        document.addEventListener("keydown", handleKeydown);
    });


</script>


<Layout>
    <!-- Wrapper to fit screen -->
    <div class="flex flex-col h-screen overflow-hidden">

        <div class="px-2 sm:px-2 lg:px-4 py-3 sm:py-2 lg:py-4 flex flex-col gap-4 flex-grow">
            <!-- Banner -->
            <div class="relative h-32 md:h-40 bg-gradient-to-br from-primary to-secondary rounded-lg md:rounded-2xl shadow-xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] hover:from-primary hover:to-cyan-600 flex items-center justify-center">              <!-- Static waves background -->
                <!-- Engineering pattern background -->
                <div class="absolute inset-0 opacity-20">
                    <svg class="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <!-- Grid lines -->
                        <path d="M 0 50 L 100 50" stroke="white" stroke-width="0.5" stroke-opacity="0.3"/>
                        <path d="M 50 0 L 50 100" stroke="white" stroke-width="0.5" stroke-opacity="0.3"/>
                        <!-- Circuit board pattern -->
                        <rect x="20" y="20" width="10" height="10" fill="none" stroke="white" stroke-width="0.7"/>
                        <rect x="70" y="60" width="10" height="10" fill="none" stroke="white" stroke-width="0.7"/>
                        <path d="M 30 30 L 40 30 L 40 40" stroke="white" stroke-width="0.7" fill="none"/>
                        <path d="M 60 70 L 70 70 L 70 80" stroke="white" stroke-width="0.7" fill="none"/>
                    </svg>
                </div>

                <!-- Content -->
                <h1 class="relative text-center text-3xl md:text-5xl font-semibold text-slate-100 drop-shadow-lg transition-transform duration-300 md:hover:scale-105">
                    Welcome to HKN Portal!
                </h1>
            </div>
        </div>
        <div class="flex flex-row flex-grow overflow-hidden min-h-0 px-6 pb-6 gap-4">
            <!-- Sidebar -->
            <div class="md:w-1/4 max-h-[40vh] overflow-auto bg-white rounded-xl shadow">
              <PointBar />
            </div>
          
            <!-- Main Content -->
            <div class="w-3/4 h-full overflow-hidden bg-white rounded-lg shadow flex flex-col relative">
              
              {#if showPopup}
                <!-- Position popup absolutely inside this container -->
                <EventPopUp event={selectedEvent} on:close={closePopup} />
              {/if}
          
              <!-- Upcoming Events -->
              <EventsCard title="Upcoming Events" subtitle={null} events={events} {handleEventClick}/>
            </div>
        </div>
    </div>
</Layout>