<script>
    import EventCalendar from "./EventCalendar.svelte";
    import EventDetailDisplay from "./EventDetailDisplay.svelte";
    import EventDisplayControlBar from "./EventDisplayControlBar.svelte";
    import EventList from "./EventList.svelte";
    import { eventstore, eventview } from "./eventstore";

    let eventsPromise = (async function getEvents() {
        // TODO
        let response = await fetch("api/events/");
        return await response.json();
    })();

    let selectedEvent;

    eventstore.subscribe((value) => {
        selectedEvent = value;
    });
</script>

<div class="eventmodule">
    <EventDisplayControlBar />
    {#await eventsPromise}
        <p>Loading...</p>
    {:then eventList}
        {#if $eventview == "list"}
            <EventList {eventList} />
        {:else if $eventview == "calendar"}
            <EventCalendar eventList={eventList} />
        {/if}
        <EventDetailDisplay {selectedEvent} />
    {:catch error}
        <p>Error: {error.message}</p>
    {/await}
</div>

<style>
    .eventmodule {
        display: grid;
        grid-template:
            "a a" max-content
            "b c" 1fr / 1fr 1fr;
        height: 80%;
        margin: 10px;
        max-width: 1000px;
    }
</style>
