<script>
    import { onMount, afterUpdate } from "svelte";
    import Layout from "../Layout.svelte";

    import PointBar from "../Components/PointBar.svelte";
    import EventsCard from "../Components/EventsCard.svelte";


    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    };

    let showSmallScreenView = false;
    let buttonLabel = "Toggle View";

    function toggleView() {
        showSmallScreenView = !showSmallScreenView;
        buttonLabel = showSmallScreenView ? "Calendar View" : "Card View";
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
            <!-- Body content goes here -->
            <EventsCard />

            </div>
        </div>
     </div>

</Layout>
