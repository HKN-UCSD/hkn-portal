<!-- File for page to fill in individual interview schedule -->
<script>
    import Layout from "../Layout.svelte";
    import { adminStatus } from '../stores.js';
    import { onMount } from "svelte";
    import { days, timeslots, AVAILABLE_COLOR } from "./interviewscheduleutils.js";

    let availability;
    let selecting = null; // Used in determining whether to set timeslot to available or unavailable

    onMount(async () => {
        // Retrieve availability of user from backend
        await getAvailability();

        // Populate the schedule according to availability retrieved
        if (availability != null) {
            populateSchedule();
        }

        // Add event listeners to each timeslot to dragging and clicking to set availabilities
        document.querySelectorAll('.timeslot').forEach(timeslot => {
            timeslot.setAttribute('draggable', true);

            /*
             * Change availability of timeslot when clicked
             * Changes background color of timeslot to AVAILABLE_COLOR if available, revert to original color if unavailable
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
                    event.target.removeAttribute('style');
                    availability[day][slotNum] = 0;
                }
            });

            /*
             * Change availability of timeslot when dragged over
             * Changes background color of timeslot to AVAILABLE_COLOR if available, revert to original color if unavailable
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
     * Changes background color of timeslot to AVAILABLE_COLOR if available, revert to original color if unavailable
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
            timeslot.removeAttribute('style');
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
     * Sets each timeslot's background color to AVAILABLE_COLOR if available, revert to original color if unavailable
     * Sets each timeslot's 'available' attribute to true if available, false if unavailable
     */
    function populateSchedule() {
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);
                if (availability[day][slotNum] == 1) {
                    timeslot.style.background = AVAILABLE_COLOR;
                    timeslot.setAttribute('available', true);
                } else {
                    timeslot.removeAttribute('style');
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
    <div class="relative flex flex-col justify-center items-center">
        <h1 class="w-full text-center text-5xl font-bold mt-10 mb-6 p-3 animate-slide-up text-primary transition-transform duration-300 hover:scale-110 hover:z-10">Interview Availability</h1>
        {#if $adminStatus}
           <a class="absolute z-20 top-4 right-4 py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105 shadow-lg bg-primary" href="/schedule">All Availabilities</a>
        {/if}
        <!-- Schedule -->
        <div class="flex flex-col justify-center overflow-x-auto text-primary">
            <table class="w-80% h-full divide-y divide-gray-200 table-auto border-separate border-spacing-x-1 border-spacing-y-0.5">
                <thead>
                    <tr>
                        <th id="empty_for_time_column" class="w-10 px-4"></th> <!-- Empty header for the time column -->
                        {#each days as day}
                            <th class="w-10 px-4 text-center">
                                <div class="flex items-center justify-center gap-2">
                                    <span>{day}</span>
                                </div>
                            </th>
                        {/each}
                    </tr>
                </thead>
                <tbody>
                    {#each timeslots as time, slot_num}
                        <tr class="h-4">
                            <!-- Time column -->
                            {#if time.includes("00")}
                                <td class="relative pl-4 pr-1 text-end items-start text-primary" rowspan=4>
                                    <span class="absolute top-0 right-1">{time}</span>
                                </td>
                            {/if}
                            <!-- Loop for days and generate cells -->
                            {#each days as day, day_num}
                                <td id="{day_num}-{slot_num}"
                                    class="h-4 w-10 mx-1 px-4 text-center bg-unavailable timeslot">
                                </td>
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </table>
            <button class="mt-4 mb-6 max-w-80% py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 transform shadow-lg bg-primary" on:click={submit}>Update</button>
        </div>
    </div>
</body>
</Layout>