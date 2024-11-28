<script>
    import Layout from "../Layout.svelte";
    import { onMount } from "svelte";
    import { generateSchedule, UNAVAILABLE_COLOR, AVAILABLE_COLOR, NUM_DAYS, NUM_SLOTS } from "./interviewscheduleutils.js";

    let availability;

    onMount(async () => {
        await getAvailability();
        generateSchedule();
        if (availability != null) {
            populateSchedule();
        }
    });

    // Make an api call to backend to retrieve availability
    async function getAvailability() {
        const response = await fetch(`/api/inductionclasses/get_availability/`);
        if (response.ok) {
            availability = await response.json();
        } else {
            availability = null;
        }
    }


</script>

<svelte:head>
    <title> HKN Portal | Availability </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
<body>
    <div style="padding-left:50px">
        <h1>Interview Availability</h1>
    </div>
    <div id="schedule"></div>
</body>
</Layout>

<style>
    #schedule {
        display: flex;
        flex-direction: row;
        padding-left: 10px;
        width: 80%;
        height: 100%;
    }
</style>