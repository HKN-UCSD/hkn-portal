<script>
    import { marked } from "marked";
    import * as purify from "dompurify";
    import EventConsole from "./EventConsole.svelte";

    export let selectedEvent;
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
    {#if content}
    <div class="description" style="display: flex; flex-direction: row">
        <p style="margin-right: 5px">Description: </p>
        {@html content}
    </div>
    {/if}
    <div class="canva-embed-code">
    {#if selectedEvent.embed_code}
        {@html selectedEvent.embed_code}
    {/if}
    </div>

    <EventConsole event={selectedEvent}/>
{/if}

<style>
    .canva-embed-code{
        width: 80%;
        max-width: 570px;
        height: auto;
        margin-bottom: 20px;
    }
    h1 > a {
        color: black;
    }
    .description :global(p) { margin-top: 0px; }
</style>
