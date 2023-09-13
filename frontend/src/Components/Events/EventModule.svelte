<script>
    import EventCalendar from "./EventCalendar.svelte";
    import EventDetailDisplay from "./EventDetailDisplay.svelte";
import EventList from "./EventList.svelte";

    let eventsPromise = (async function getEvents() {
        // TODO
        let response = await fetch("api/events/");
        return await response.json();
    })();

    let selectedEvent = null;
</script>

<div class="eventmodule">
    <div class="viewmodearray">
        <button>List</button>
        <button>Calendar</button>
    </div>

    {#await eventsPromise}
        <p>Loading...</p>
    {:then eventList} 
        <EventList eventList={eventList}/>
        <!-- <EventCalendar eventList={eventList} /> -->
        <EventDetailDisplay {selectedEvent}/>
    {:catch error}
        <p>Error: {error.message}</p>
    {/await}
    </div>

<style>
    .eventmodule {
        display: grid;
        grid-template: 
            "a a" max-content
            "b c" 1fr
            ;
        height: 80%;
        margin: 10px;

    }
    .viewmodearray {
        grid-area: a;
        display: flex;
        justify-content: right;
        margin: 10px;
    }
</style>