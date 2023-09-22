<script>
    import { getEvent } from "../Components/Events/eventstore";
    import EventDetailContent from "../Components/Events/EventDetailContent.svelte";
    export let id;
</script>
{#await getEvent(id)}
    <p>Loading...</p>
{:then selectedEvent} 
    <EventDetailContent selectedEvent={selectedEvent} />
{:catch error}
    <p>Error: {error.message}</p>
{/await}