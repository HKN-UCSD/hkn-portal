<script>
    import { eventstore } from "./eventstore";
    export let eventdata;
    // Convert start/end data into a brief, human-readable representation
    let start_date = new Date(eventdata.start_time);
    let end_date = new Date(eventdata.end_time);
</script>

<button
    class="eventlistitem"
    class:selected={eventdata === $eventstore}
    class:faded={end_date.getTime() < new Date().getTime()}
    type="button"
    on:click={() => {
        if (eventdata === $eventstore) {
            eventstore.set(undefined);
        } else {
            eventstore.set(eventdata);
        }
    }}
>
    <h4 class="title">{eventdata.name}</h4>
    <p class="category">
        {eventdata.event_type == null ? "None" : eventdata.event_type.name}
    </p>
</button>

<style>
    /* TODO */
    .eventlistitem {
        border-radius: 5px;
        border: none;
        padding: 10px 5%;
        box-shadow: 0px 1px 2px 1px lightgrey;
        width: 100%;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        overflow: hidden;
        cursor: pointer;
    }

    h4 {
        /* h1, h2, h3, h4, h5, h6 { */
        padding: 0px;
        margin: 0px;
    }
    .title,
    .category {
        margin: 0px 10px;
    }
    .selected {
        background-color: var(--primary-color);
        color: white;
    }
    .faded {
        opacity: 0.5;
    }
</style>
