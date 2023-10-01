<script>
    import { getEvent } from "../Components/Events/eventstore";
    import EventDetailContent from "../Components/Events/EventDetailContent.svelte";
    export let id;
</script>

<div>
    {#await getEvent(id)}
        <p>Loading...</p>
    {:then selectedEvent}
        <EventDetailContent {selectedEvent} />
    {:catch error}
        <p>Error: {error.message}</p>
    {/await}
</div>

<style>
    div {
        padding: 30px;
        padding-top: 10px;
        margin: 30px;
    }
</style>
