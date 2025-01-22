<script>
    import { onMount, afterUpdate } from "svelte";
    import { navigate } from "svelte-routing";
    import EventCalendar from "../Components/Events/EventCalendar.svelte";
    import EventCard from "../Components/Events/EventCard.svelte";
    import Layout from "../Layout.svelte";


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

    onMount(() => {
        // Check window size on mount and set the initial view based on the small screen condition
        showSmallScreenView = window.innerWidth <= 768;

        // Add a resize event listener to dynamically update showSmallScreenView variable
        window.addEventListener("resize", () => {
            showSmallScreenView = window.innerWidth <= 768;
        });
    });

    // Update buttonLabel when showSmallScreenView changes
    afterUpdate(() => {
        buttonLabel = showSmallScreenView ? "Calendar View" : "Card View";
    });
</script>


<svelte:head>
    <title> HKN Portal | Home </title>
</svelte:head>

<Layout>

    <div class="parent">
        <div class="left">
            {#await getPermissions()}
                <p>Loading...</p>
            {:then permissions}
                {#if permissions.is_admin}
                    <button class="button" on:click={() => navigate("/events/create/")}>
                        Create Event
                    </button>
                {/if}
            {:catch error}
                <p>Error: {error.message}</p>
            {/await}
        </div>
        {#if showSmallScreenView}
            <div class="center"><h1>Upcoming Events</h1></div>
        {:else}
            <div class="center"><h1>Events</h1></div>
        {/if}
        <div class="right">
            <!-- Add a button to toggle view -->
            <button class="toggle-button" on:click={toggleView}>
                {buttonLabel}
            </button>
        </div>
    </div>

    <div class="main-content">
        {#if showSmallScreenView}
            <div class="eventcard">
                <EventCard />
            </div>
        {:else}
            <div class="calendar">
                <EventCalendar />
            </div>
        {/if}
    </div>
</Layout>
