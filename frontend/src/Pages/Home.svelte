<script>
    import EventCalendar from "../Components/Events/EventCalendar.svelte";
</script>

<main>
    <div class="banner-container">
        <img src="/static/Banner.png" alt="Club Banner" class="banner"/>
    </div>

    <center><h1>Events</h1></center>
    
    <div class="calendar">
        <EventCalendar/>
    </div>
</main>

<style>
    .banner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 25px 25px 0px 25px;
    }

    .banner {
        max-width: 100%; /* Ensures the banner isn't larger than its container */
        height: auto;    /* Maintains aspect ratio */
    }

    .calendar {
        padding: 10px 10px;
        border-radius: 5px;
        box-shadow: 0px 1px 2px 1px lightgrey;
        grid-area: c;
        margin: 10px;
        background-color: #f5f5f5;
    }

    /* Add any other styles as needed */
</style>