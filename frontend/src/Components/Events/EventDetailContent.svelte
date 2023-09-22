<script>
    import { marked } from "marked";
    import * as purify from "dompurify";

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
    <h2>{selectedEvent.name}</h2>
    <p>
        Category: {selectedEvent.event_type == null
            ? "None"
            : selectedEvent.event_type}
    </p>
    {#if last_modified}
        <p>Last modified {last_modified.toDateString()}</p>
    {/if}
    {#if start_time}
        <p><span>Starts {start_time.toLocaleString()}</span></p>
    {/if}
    {#if end_time}
        <p><span>Ends {end_time.toLocaleString()}</span></p>
    {/if}
    <br />
    {@html content}
{/if}