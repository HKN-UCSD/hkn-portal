<script>
    import Layout from "../Layout.svelte";
    import { onMount } from "svelte";
    import { generateSchedule, UNAVAILABLE_COLOR, AVAILABLE_COLOR, NUM_DAYS, NUM_SLOTS } from "./interviewscheduleutils.js";

    let availability;
    let selecting = null;

    onMount(async () => {
        await getAvailability();
        generateSchedule();
        if (availability != null) {
            populateSchedule();
        }

        document.querySelectorAll('.timeslot').forEach(timeslot => {
            timeslot.setAttribute('draggable', true);

            timeslot.addEventListener('click', (event) => {
                if (event.target.getAttribute('available') == 'false') {
                    event.target.setAttribute('available', true);
                    event.target.style.background = AVAILABLE_COLOR;
                } else if (event.target.getAttribute('available') == 'true') {
                    event.target.setAttribute('available', false);
                    event.target.style.background = UNAVAILABLE_COLOR;
                }
            });

            timeslot.addEventListener('mouseenter', (event) => {
                if (event.buttons === 1) {
                    toggleTimeslot(timeslot);
                }
            });
        });

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
            console.log('selecting: true');
            timeslot.style.background = AVAILABLE_COLOR;
            availability[day][slotNum] = 1;
        } else {
            console.log('selecting: false');
            timeslot.style.background = UNAVAILABLE_COLOR;
            availability[day][slotNum] = 0;
        }
        timeslot.setAttribute('available', selecting);
    }

    // Make an api call to backend to retrieve availability
    async function getAvailability() {
        const response = await fetch(`/api/inductionclasses/get_availability/`);
        if (response.ok) {
            availability = await response.json();
        } else {
            availability = null;
        }
    }

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

    async function submit() {
        let CSRFToken = document.cookie
            .split("; ")
            .find((element) => element.startsWith("csrftoken="))
            .split("=")[1];
        console.log(availability);
        let data = {
            'availability': availability
        }
        const response = await fetch(`/api/inductionclasses/set_availability/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRFToken,
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            console.log('Availability updated');
        } else {
            console.log('Failed to update availability');
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
    <div style="display: flex; flex-direction: row;">
        <div id="schedule"></div>
        <button on:click={submit}>Submit</button>
    </div>
</body>
</Layout>

<style>
    #schedule {
        display: flex;
        flex-direction: row;
        padding-left: 50px;
        padding-bottom: 3vh;
        width: 80%;
        height: 100%;
    }
</style>