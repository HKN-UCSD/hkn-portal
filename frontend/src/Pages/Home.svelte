<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";

    import PointBar from "../Components/PointBar.svelte";
    import EventsCard from "../Components/EventsCard.svelte";
    import EventPopUp from "../Components/EventPopUp.svelte";
    let showPopup = false;
    let selectedEvent = null;
    

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
        events = res.filter(event => event.start_time > curr).map(event => ({title: event.name, description: event.description, id: event.pk, url: `/events/${event.pk}`}));
    });


    function openEvent(event) {// Debugging log
        console.log("OPENING", event)
        selectedEvent = event; // Ensures reactivity
        showPopup = true;
    }
    
    function closeEvent() {
        selectedEvent = null;
        showPopup = false;
    }
</script>


<Layout>

    <div class="flex flex-col mt-10 ">
        <h1 class="w-full text-center text-5xl font-bold mb-6 animate-slide-up text-primary transition-transform duration-300 hover:scale-110 active:text-secondary">Welcome back! </h1>
        <div class="flex flex-col md:flex-row mt-5 overflow-auto gap-7">
            <!-- Sidebar -->
            <div class="md:w-1/4 mb-5" ref="left">
            <PointBar />
            </div>

            <!-- Main Content -->
            <div class="md:w-3/4 bg-white">
            {#if selectedEvent}
                <EventPopUp event={selectedEvent} close={closeEvent} />
            {/if}
            <!-- Body content goes here -->
            <!-- <EventsCard title="Upcoming Events" subtitle={null} events={events}/> -->
            <EventsCard title="Upcoming Events" subtitle={null} events={events} on:eventClick={openEvent} />

            </div>
        </div>
    </div>

    

</Layout>
