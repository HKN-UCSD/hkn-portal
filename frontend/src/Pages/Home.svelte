<script>
    import { onMount } from "svelte";
    import { getEvents } from "../Components/Events/eventstore";
    import Layout from "../Layout.svelte";

    import PointBar from "../Components/PointBar.svelte";
    import EventsCard from "../Components/Events/EventsCard.svelte";
    import { embedCode } from "../Components/Events/canvaEmbed";


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
        console.log(res);
        events = res.filter(event => event.start_time > curr).map(event => ({
            title: event.name,
            description: event.description,
            start_time: event.start_time,
            end_time: event.end_time,
            location: event.location,
            pk: event.pk, url: `/events/${event.pk}`,
            embed_code: event.embed_code ? event.embed_code : embedCode[event.event_type]

        }
        ));
        console.log(events);

    });


</script>


<Layout>
  <div class="relative md:w-full mx-5 md:mx-auto mb-6 relative mt-3 md:mt-6 lg:mt-10">
    <div class="relative h-48 md:h-64 bg-gradient-to-br from-primary to-secondary rounded-lg md:rounded-2xl shadow-xl p-8 transition-all duration-300 hover:shadow-2xl hover:scale-[1.02] hover:from-primary hover:to-cyan-600 flex items-center justify-center">              <!-- Static waves background -->
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
        <h1 class="relative text-center text-4xl md:text-6xl font-semibold text-slate-100 drop-shadow-lg transition-transform duration-300 md:hover:scale-105">
            Welcome to HKN Portal!
        </h1>
    </div>
  </div>
        <div class="flex flex-col md:flex-row md:mt-5 lg:mt-10 overflow-auto gap-7">
            <!-- Sidebar -->
            <div class="md:w-1/4" ref="left">
            <PointBar />
            </div>

            <!-- Main Content -->
            <div class="md:w-3/4 bg-white">
            <!-- Body content goes here -->
            <EventsCard title="Upcoming Events" subtitle={null} events={[]}/>

            </div>
        </div>


</Layout>