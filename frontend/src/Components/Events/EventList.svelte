<script>
    // TODO
    import EventListItem from "./EventListItem.svelte";
    import {eventview} from "./eventstore"

    export let eventList = [];

</script>

<div class="eventlistdisplay" class:displayhidden={eventview == "list"}>
    {#each eventList as eventdata}
        <EventListItem {eventdata}/>
    {/each}
</div>

<style>
    .eventlistdisplay {
        grid-area: b;
        margin: 10px;
    }
</style>