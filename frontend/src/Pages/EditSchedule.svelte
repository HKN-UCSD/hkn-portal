<!-- File for page to fill in individual interview schedule -->
<script>
    import Layout from "../Layout.svelte";
    import { adminStatus } from '../stores.js';
    import { onMount } from "svelte";
    import { generateSchedule, UNAVAILABLE_COLOR, AVAILABLE_COLOR, NUM_DAYS, NUM_SLOTS } from "./interviewscheduleutils.js";

    let availability;
    let selecting = null; // Used in determining whether to set timeslot to available or unavailable

    onMount(async () => {
        // Retrieve availability of user from backend
        await getAvailability();

        // Generate table for schedule
        generateSchedule();

        // Populate the schedule according to availability retrieved
        if (availability != null) {
            populateSchedule();
        }

        // Add event listeners to each timeslot to dragging and clicking to set availabilities
        document.querySelectorAll('.timeslot').forEach(timeslot => {
            timeslot.setAttribute('draggable', true);

            /*
             * Change availability of timeslot when clicked
             * Changes background color of timeslot to AVAILABLE_COLOR if available, UNAVAILABLE_COLOR if unavailable
             * Changes 'available' attribute of timeslot to true if available, false if unavailable
             */
            timeslot.addEventListener('click', (event) => {
                let day = timeslot.id.split('-')[0];
                let slotNum = timeslot.id.split('-')[1];
                if (event.target.getAttribute('available') == 'false') {
                    event.target.setAttribute('available', true);
                    event.target.style.background = AVAILABLE_COLOR;
                    availability[day][slotNum] = 1;
                } else if (event.target.getAttribute('available') == 'true') {
                    event.target.setAttribute('available', false);
                    event.target.style.background = UNAVAILABLE_COLOR;
                    availability[day][slotNum] = 0;
                }
            });

            /*
             * Change availability of timeslot when dragged over
             * Changes background color of timeslot to AVAILABLE_COLOR if available, UNAVAILABLE_COLOR if unavailable
             * Changes 'available' attribute of timeslot to true if available, false if unavailable
             */
            timeslot.addEventListener('mouseenter', (event) => {
                if (event.buttons === 1) { // Left mouse button is pressed
                    toggleTimeslot(timeslot);
                }
            });
        });

        /*
         * Listen for start of drag event
         * Sets selecting to true if timeslot starts unavailable, false if available
         */
        document.addEventListener('dragstart', (event) => {
            event.preventDefault();
            if (event.target.classList.contains('timeslot')) {
                let timeslot = event.target;
                if (timeslot.getAttribute('available') == 'false') {
                    selecting = true;
                } else if (timeslot.getAttribute('available') == 'true') {
                    selecting = false;
                }
                toggleTimeslot(timeslot);
            }
        });
    });

    /*
     * Change availability of timeslot
     * Changes background color of timeslot to AVAILABLE_COLOR if available, UNAVAILABLE_COLOR if unavailable
     * Changes 'available' attribute of timeslot to true if available, false if unavailable
     * 
     * @param {timeslot} The timeslot (document object) to change availability of
     */
    function toggleTimeslot(timeslot) {
        if (selecting == null) {
            return;
        }
        if (timeslot.getAttribute('available') == selecting) {
            return;
        }

        let day = timeslot.id.split('-')[0];
        let slotNum = timeslot.id.split('-')[1];

        if (selecting == true) {
            timeslot.style.background = AVAILABLE_COLOR;
            availability[day][slotNum] = 1;
        } else {
            timeslot.style.background = UNAVAILABLE_COLOR;
            availability[day][slotNum] = 0;
        }
        timeslot.setAttribute('available', selecting);
    }

    /**
     * Retrieve availability array from backend
     * availability = null if error occurs
     */
    async function getAvailability() {
        const response = await fetch(`/api/inductionclasses/get_availability/`);
        if (response.ok) {
            availability = await response.json();
        } else {
            availability = null;
        }
    }

    /*
     * Go through availability array and update schedule accordingly
     * Sets each timeslot's background color to AVAILABLE_COLOR if available, UNAVAILABLE_COLOR if unavailable
     * Sets each timeslot's 'available' attribute to true if available, false if unavailable
     */
    function populateSchedule() {
        for (let day = 0; day < NUM_DAYS; day++) {
            for (let slotNum = 0; slotNum < NUM_SLOTS; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);
                if (availability[day][slotNum] == 1) {
                    timeslot.style.background = AVAILABLE_COLOR;
                    timeslot.setAttribute('available', true);
                } else {
                    timeslot.style.background = UNAVAILABLE_COLOR;
                    timeslot.setAttribute('available', false);
                }
            }
        }
    }

    /**
     * Submit availability to backend
     */
    async function submit() {
        let CSRFToken = document.cookie
            .split("; ")
            .find((element) => element.startsWith("csrftoken="))
            .split("=")[1];

        let data = {
            'availability': availability
        }

        // Make a POST request to backend to update availability
        const response = await fetch(`/api/inductionclasses/set_availability/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRFToken,
            },
            body: JSON.stringify(data)
        });

        // User feedback
        if (response.ok) {
            alert('Availability updated');
        } else {
            alert('Failed to update availability');
        }
    }
</script>

<svelte:head>
    <title> HKN Portal | Availability </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>
<Layout>
<body>
    <div style="margin-left: 50px; width: 85%; display: flex; align-items: center; justify-content: space-between;">
        <h1 style="margin-left: 15px">Interview Availability</h1>
        {#if $adminStatus}
           <a id="scheduleOverview" href="/schedule">All Availabilities</a>
        {/if}
    </div>
    <div style="display: flex; flex-direction: row;">
        <div id="schedule"></div>
        <button id="submit" on:click={submit}>Submit</button>
    </div>
</body>
</Layout>

<style>
    #scheduleOverview{
      color: white;
      margin-left: 15px;
      margin-bottom: 20px;
      border-radius: 0.25em;
      padding: 0.4em 0.65em;
      background-color: var(--fc-button-bg-color);
      border: none;
      outline: none;
   }
    #schedule {
        display: flex;
        flex-direction: row;
        padding-left: 50px;
        padding-bottom: 3vh;
        height: 100%;
    }
    #submit {
        text-align: center;
        margin-left: 20px;
        margin-top: 20px;
        padding: 7px;
        font-size: 16px;
        height: 5vh;
    }
</style>