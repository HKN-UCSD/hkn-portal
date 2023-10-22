<script>
    import { onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import EventCalendar from "../Components/Events/EventCalendar.svelte";
    import EventCard from "../Components/Events/EventCard.svelte";



    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    };

    let isSmallScreen = false;
    
    // Check window size on mount and set the isSmallScreen variable
    onMount(() => {
        isSmallScreen = window.innerWidth <= 768;
    });

    // Add a resize event listener to dynamically update isSmallScreen variable
    window.addEventListener("resize", () => {
        isSmallScreen = window.innerWidth <= 768;
    });
</script>

<svelte:head>
    <title> HKN Portal | Home </title>
</svelte:head>

<main>
    <title> HKN | Member Portal </title>
    <div class="banner-container">
        <img src="/static/Banner.png" alt="Club Banner" class="banner"/>
    </div>

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
        {#if isSmallScreen}
            <div class="center"><h1>Upcoming Events</h1></div>
        {:else}
            <div class="center"><h1>Events</h1></div>
        {/if}
        <div class="right"></div>
    </div>
    <div class="main-content">
        {#if isSmallScreen}
            <div class="eventcard">
                <EventCard />
            </div>
        {:else}
            <div class="calendar">
                <EventCalendar />
            </div>
        {/if}
    </div>
</main>

<style>
    .banner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 25px 25px 0px 25px;
    }

    .banner {
        max-width: 100%; /* Ensures the banner isn't larger than its container */
        height: auto;    /* Maintains aspect ratio */
    }

    .calendar {
        padding: 10px 10px;
        border-radius: 5px;
        box-shadow: 0px 1px 2px 1px lightgrey;
        grid-area: c;
        margin: 10px;
        background-color: #f5f5f5;
    }

    .parent {
        display: flex;
    }
    .left, .right {
        flex: 1;
        display: flex;
        align-items: center;
    }

    button {
        margin-left: 25px;
    }

</style>