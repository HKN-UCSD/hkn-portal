<script>
    import { marked } from "marked";
    import DOMPurify from "dompurify";
    import CustomizableEventConsole from "./CustomizableEventConsole.svelte";
    import { eventGraphics } from "./EventGraphics.js";

    export let selectedEvent;
    $: start_time = new Date(selectedEvent?.start_time);
    $: end_time = new Date(selectedEvent?.end_time);
    $: last_modified = new Date(selectedEvent?.time_last_modified);
    $: content =
        selectedEvent == null
            ? ""
            : DOMPurify.sanitize(marked.parse(selectedEvent?.description));


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

    {#if !selectedEvent.is_time_restricted}
    <p>This event can be signed into at any time.</p>
    {/if}
   {#if content}
    <div class="description">
        <p>Description:
            {@html content}
        </p>
    </div>
    {/if}

    <div class="canva-embed-code">
        {#if selectedEvent.embed_code}
            {@html selectedEvent.embed_code}
        {:else if Object.keys(eventGraphics).includes(selectedEvent.event_type)}
            {@html eventGraphics[selectedEvent.event_type]}
        {/if}
    </div>

    <CustomizableEventConsole event={selectedEvent}/>
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
    .description {
        word-wrap: break-word;
        white-space: pre-wrap;
        word-break: break-word;
    }

    .description p {
        margin: 0;
        display: inline;
    }

</style>

