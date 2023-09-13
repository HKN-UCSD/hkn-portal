<script>
    // TODO
    import EventListItem from "./EventListItem.svelte";

    export let eventList = [];
    console.log(eventList)

</script>

<div class="eventlistdisplay">
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