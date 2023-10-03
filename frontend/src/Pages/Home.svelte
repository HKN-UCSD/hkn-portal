<script>
    import EventCalendar from "../Components/Events/EventCalendar.svelte";
    import { navigate } from "svelte-routing";

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    };
</script>

<main>
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
        <div class="center"><h1>Events</h1></div>
        <div class="right"></div>
    </div>
    
    <div class="calendar">
        <EventCalendar/>
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

    .button {
        background-color: rgb(0,100,200);
        border: none;
        color: white;
        text-align: center;
        font-size: 16px;
        margin-left: 30px;
    }

</style>