<!-- This file uses constants imported from InterviewSchedule.svelte -->
<script>
    import { onMount } from "svelte";
    import Layout from "../Layout.svelte";
    import { generateSchedule } from "./interviewscheduleutils.js";

    
</script>

<svelte:head>
    <title> HKN Portal | Availability </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>
<Layout>
<body onload="generateTable()">
    <script>
        let availability;
        
        async function getAvailability() {
            const response = await fetch(`/api/availability/self/`);
            availability = await response.json();
        }

        function applyAvailability(availability) {
            for (const time of availability) {
                const cell = document.getElementById(time);
                cell.style.backgroundColor = "green";
            }
        }
        
    </script>
    <div style="padding-left:50px">
        <h1>Interview Availability</h1>
    </div>
    <div id="schedule"></div>
</body>
</Layout>