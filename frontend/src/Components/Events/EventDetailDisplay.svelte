<script>
    import { eventstore } from "./eventstore";
    import { marked } from "marked";
    import * as purify from "dompurify";
    // const DOMPurify = createDomPurify(window)

    // process into more human-readable times
    let selectedEvent = null;
    eventstore.subscribe((value) => {
        selectedEvent = value;
    });

    $: start_time = new Date(selectedEvent?.start_time);
    $: end_time = new Date(selectedEvent?.end_time);
    $: last_modified = new Date(selectedEvent?.time_last_modified);
    $: content =
        selectedEvent == null
            ? ""
            : purify.sanitize(marked.parse(selectedEvent?.description));
</script>

<div class="eventdetaildisplay" class:hidden={selectedEvent == null}>
    {#if selectedEvent != null}
        <h2>{selectedEvent.name}</h2>
        <p>
            Category: {selectedEvent.event_type == null
                ? "None"
                : selectedEvent.event_type.name}
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
