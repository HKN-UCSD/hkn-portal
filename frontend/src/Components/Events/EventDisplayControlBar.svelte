<script>
    import {eventview} from './eventstore'
</script>
<div class="controlbar">
    <h1> Events</h1>
    <div class="filterarray">
        <!-- TODO -->
    </div>
    <div class="viewmodearray">
        <button on:click={() => {eventview.set("list")}}>List</button>
        <button on:click={() => {eventview.set("calendar")}}>Calendar</button>
    </div>
</div>

<style>
    .controlbar {
        grid-area: a;
        display: flex;
        flex-direction: row;
    }

    .viewmodearray {
        display: flex;
        justify-content: right;
        margin: 10px;
        flex-grow: 1;
    }

    .viewmodearray button {
        height: fit-content;
    }
</style>
