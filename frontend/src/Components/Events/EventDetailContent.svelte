<script>
    import { marked } from "marked";
    import * as purify from "dompurify";
    import EventActionButton from "./EventActionButton.svelte";
    import { getEventActions } from "./eventstore";

    export let selectedEvent;
    $: start_time = new Date(selectedEvent?.start_time);
    $: end_time = new Date(selectedEvent?.end_time);
    $: last_modified = new Date(selectedEvent?.time_last_modified);
    $: content =
        selectedEvent == null
            ? ""
            : purify.sanitize(marked.parse(selectedEvent?.description));

    let actionresulttext = "";
    let actionmessageclass = "nothing";

    function handleEventActionComplete(event) {
        console.log(event);
        if ("detail" in event.detail) {
            actionresulttext = event.detail.detail;
            actionmessageclass = "error";
        } else if ("message" in event.detail) {
            actionresulttext = event.detail.message;
            actionmessageclass = "message";
        }
    }

    function eventNameMap(eventName) {
        let namemap = {
            rsvp: "RSVP",
            signin: "Sign In",
        };
        return namemap[eventName];
    }
</script>

{#if selectedEvent != null}
    <h1><a href="/events/{selectedEvent.pk}">{selectedEvent.name}</a></h1>
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

    {#await getEventActions()}
        <p>Loading buttons...</p>
    {:then eventActions}
        {#each eventActions as eventAction}
            <EventActionButton
                event={selectedEvent}
                action={eventAction.name}
                on:eventactioncomplete={handleEventActionComplete}
            >
                {eventNameMap(eventAction.name)}
            </EventActionButton>
        {/each}
        <p class="actionmessage {actionmessageclass}">{actionresulttext}</p>
    {/await}
    {@html content}
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
</style>
