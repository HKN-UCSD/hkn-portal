<script>
    import EventCalendar from "./EventCalendar.svelte";
</script>

<main>
    <div class="banner-container">
        <img src="/static/frontend/Banner.png" alt="Club Banner" class="banner"/>
    </div>
    
    <EventCalendar/>
</main>

<style>
    .banner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 20px;  /* Adjust as needed for spacing below the banner */
    }

    .banner {
        max-width: 100%; /* Ensures the banner isn't larger than its container */
        height: auto;    /* Maintains aspect ratio */
    }

    /* Add any other styles as needed */
</style>