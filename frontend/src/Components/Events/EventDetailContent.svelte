<script>
    import { marked } from "marked";
    import * as purify from "dompurify";
    import EventConsole from "./EventConsole.svelte";

    export let selectedEvent;
    console.log(selectedEvent.event_photo);
    $: start_time = new Date(selectedEvent?.start_time);
    $: end_time = new Date(selectedEvent?.end_time);
    $: last_modified = new Date(selectedEvent?.time_last_modified);
    $: content =
        selectedEvent == null
            ? ""
            : purify.sanitize(marked.parse(selectedEvent?.description));
</script>

{#if selectedEvent != null}
    <h1><a href="/events/{selectedEvent.pk}">{selectedEvent.name}</a></h1>
    <p>
        Category: {selectedEvent.event_type == null
            ? "None"
            : selectedEvent.event_type}
    </p>
    <p>Last modified {last_modified.toDateString()}</p>
    <p><span>Starts {start_time.toLocaleString()}</span></p>
    <p><span>Ends {end_time.toLocaleString()}</span></p>
    <p>Location: {selectedEvent.location}</p>
    <p>Points: {selectedEvent.points}</p>
    <img class="image" src="{selectedEvent.event_photo}" alt={selectedEvent.title}>
    {#if content}
    <div class="description" style="display: flex; flex-direction: row">
        <p style="margin-right: 5px">Description: </p>
        {@html content}
    </div>
    {/if}

    <EventConsole event={selectedEvent}/>
{/if}

<style>
    h2,
    h1 > a {
        color: black;
    }
    .actionmessage {
        border-radius: 10px;
        color: white;
        padding: 10px;
    }
    .actionmessage.nothing {
        display: none;
    }
    .actionmessage.error {
        background-color: red;
    }
    .actionmessage.message {
        background-color: var(--primary-color);
    }

    .description :global(p) { margin-top: 0px; }
</style>
