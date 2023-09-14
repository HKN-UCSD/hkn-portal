<script>
    import { eventstore } from "./eventstore";

    // process into more human-readable times
    let selectedEvent;
    eventstore.subscribe((value) => {
        selectedEvent = value;
    })

    $: start_time = selectedEvent?.start_time;
    $: end_time = selectedEvent?.end_time;
    $: last_modified = selectedEvent?.time_tlast_modified;
</script>

<div class="eventdetaildisplay" class:hidden={selectedEvent == null}>
    {#if selectedEvent != null}
        <h3>{selectedEvent.name}</h3>
        <p>{selectedEvent.event_type.name}</p>
        {#if last_modified}
        <p>Last modified {last_modified}</p>
        {/if}
        {#if start_time && end_time}
            <p><span>{start_time}</span> - <span>{end_time}</span></p>
        {:else if start_time}
            <p><span>Starts {start_time}</span></p>
        {:else if end_time}
            <p><span>Ends {end_time}</span></p>
        {/if}
        <p>{selectedEvent.description}</p>
    {/if}
</div>

<style>
    .eventdetaildisplay {
        border-radius: 5px;
        box-shadow: 0px 1px 2px 1px lightgrey;
        grid-area: c;
        margin: 10px;
        padding: 30px;
    }
    .hidden {
        visibility: hidden;
    }

</style>
