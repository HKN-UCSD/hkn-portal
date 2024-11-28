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

    // Populate the schedule with availability
    function addAvailability() {
        for (let i = 0; i < NUM_DAYS; i++) {
            for (let j = 0; j < NUM_SLOTS; j++) {
                const cell = document.getElementById(`cell-${i}-${j}`);
                if (availability[i][j] === 0) {
                    cell.style.backgroundColor = UNAVAILABLE_COLOR;
                } else {
                    cell.style.backgroundColor = AVAILABLE_COLOR;
                }
            }
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