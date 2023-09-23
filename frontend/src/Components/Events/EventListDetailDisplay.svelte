<script>
    import { eventstore } from "./eventstore";
    import EventDetailContent from "./EventDetailContent.svelte";
    // const DOMPurify = createDomPurify(window)

    // process into more human-readable times
    let selectedEvent = null;
    eventstore.subscribe((value) => {
        selectedEvent = value;
    });

    console.log(selectedEvent);
</script>

<div class="eventdetaildisplay" class:hidden={selectedEvent == null}>
    <EventDetailContent selectedEvent={selectedEvent}/>
</div>

<style>
    .eventdetaildisplay {
        border-radius: 5px;
        box-shadow: 0px 1px 2px 1px lightgrey;
        grid-area: c;
        margin: 10px;
        padding: 40px;
    }
    .hidden {
        visibility: hidden;
    }
</style>
