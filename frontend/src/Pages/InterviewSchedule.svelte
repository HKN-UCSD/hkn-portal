<!-- File for displaying overall interview schedule -->
<script>
    import Layout from "../Layout.svelte";
    import { onMount } from "svelte";
    import { generateSchedule, UNAVAILABLE_COLOR, AVAILABLE_COLOR, SELECTED_COLOR, NUM_DAYS, NUM_SLOTS } from "./interviewscheduleutils.js"

    let availabilities = null;
    let selected_slot = null;

    onMount(async () => {
        await getAvailabilities();
        generateSchedule();
        if (availabilities != null) {
            populateSchedule();
        }

        // Add event listener to document to manage clicks on timeslots
        document.addEventListener('click', function(event) {
            // No previously selected slot
            if (selected_slot == null) {
                if (event.target.classList.contains('timeslot')) {
                    selected_slot = event.target.id;
                    event.target.style.background = SELECTED_COLOR;
                    setAvailabilityDisplay(event.target.id);
                    return;
                }
            } else {
                let timeslot = document.getElementById(selected_slot);
                let day = timeslot.id.split('-')[0];
                let slot = timeslot.id.split('-')[1];
                // Clicked on same slot, unselect
                if (event.target.id == selected_slot) {
                    selected_slot = null;
                    try {
                        if (availabilities[day][slot]['inductees'].length != 0) {
                            timeslot.style.background = AVAILABLE_COLOR;
                        } else {
                            timeslot.style.background = UNAVAILABLE_COLOR;
                        }
                    } catch {
                        timeslot.style.background = UNAVAILABLE_COLOR;
                    }
                    setAvailabilityDisplay(event.target.id);
                } else if (event.target.classList.contains('timeslot')) {
                    // Clicked on another slot
                    selected_slot = event.target.id;
                    // Reset previously selected slot
                    try {
                        if (availabilities[day][slot]['inductees'].length != 0) {
                            timeslot.style.background = AVAILABLE_COLOR;
                        } else {
                            timeslot.style.background = UNAVAILABLE_COLOR;
                        }
                    } catch {
                        timeslot.style.background = UNAVAILABLE_COLOR;
                    }
                    event.target.style.background = SELECTED_COLOR;
                    setAvailabilityDisplay(event.target.id);
                } else {
                    // Clicked elsewhere
                    try {
                        if (availabilities[day][slot]['inductees'].length != 0) {
                            timeslot.style.background = AVAILABLE_COLOR;
                        } else {
                            timeslot.style.background = UNAVAILABLE_COLOR;
                        }
                    } catch {
                        timeslot.style.background = UNAVAILABLE_COLOR;
                    }
                    selected_slot = null;
                    clearAvailabilityDisplay();
                }
            }
        });
    });

    // Make an api call to the backend to retrieve all availabilities
    async function getAvailabilities() {
        const response = await fetch(`api/inductionclasses/all_availabilities/`);
        if (response.ok) {
            availabilities = await response.json();
        } else {
            availabilities = null;
        }
        console.log(availabilities);
    }

    // Sets the availability display for the selected timeslot
    function setAvailabilityDisplay(id) {
        let day = id.split('-')[0];
        let slot = id.split('-')[1];

        clearAvailabilityDisplay();
        let inductees;
        let officers;
        try {
            inductees = availabilities[day][slot]['inductees'];
            officers = availabilities[day][slot]['officers'];
        } catch {
            return;
        }
        
        let available_inductees = document.getElementById('available_inductees');
        let available_officers = document.getElementById('available_officers');

        const P_STYLE = "margin: 1px 0px 1px 0px;";
        inductees.forEach(inductee => {
            let name = document.createElement('p');
            name.innerText = inductee;
            name.style = P_STYLE;
            available_inductees.appendChild(name);
        });
        officers.forEach(officer => {
            let name = document.createElement('p');
            name.innerText = officer;
            name.style = P_STYLE;
            available_officers.appendChild(name);
        });
    }

    // Clears all names in the timeslot availability display
    function clearAvailabilityDisplay() {
        let available_inductees = document.getElementById('available_inductees');
        while(available_inductees.firstChild) {
            available_inductees.removeChild(available_inductees.firstChild);
        }
        let available_officers = document.getElementById('available_officers');
        while(available_officers.firstChild) {
            available_officers.removeChild(available_officers.firstChild);
        }
    }

    /*
     * Make slots with inductee availabilities blue
     * Attach mouseover and mouseout events on slots with availabilties
     */
    function populateSchedule() {
        for (let day = 0; day < NUM_DAYS; day++) {
            for (let slotNum = 0; slotNum < NUM_SLOTS; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);
                // Make timeslot colored if an inductee has availability
                if (availabilities[day][slotNum]['inductees'].length != 0) {
                    timeslot.style.background = AVAILABLE_COLOR;
                    timeslot.setAttribute('available', true);
                }
                // Add mouseover event listener to display inductees and officers at timeslot
                timeslot.addEventListener('mouseover', function() {
                    const P_STYLE = "margin: 1px 0px 1px 0px;";
                    if (selected_slot != null) {
                        return;
                    }
                    clearAvailabilityDisplay();
                    let inductees = availabilities[day][slotNum]['inductees'];
                    let available_inductees = document.getElementById('available_inductees');
                    inductees.forEach(inductee => {
                        let name = document.createElement('p');
                        name.innerText = inductee;
                        name.style = P_STYLE;
                        available_inductees.appendChild(name);
                    });
                    let officers = availabilities[day][slotNum]['officers'];
                    let available_officers = document.getElementById('available_officers');
                    officers.forEach(officer => {
                        let name = document.createElement('p');
                        name.innerText = officer;
                        name.style = P_STYLE;
                        available_officers.appendChild(name);
                    })
                });

                // Add mouseout event listener to clear availability display
                timeslot.addEventListener('mouseleave', function() {
                    if (selected_slot != null) {
                        return;
                    }
                    clearAvailabilityDisplay();
                });
            }
        }
    }
</script>

<svelte:head>
    <title> HKN Portal | Interview Schedule </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
<body>
    <div style="padding-left:50px">
        <h1>Overall Schedule</h1>
    </div>
    <div style="display: flex; flex-direction: row;">
        <div id="slot_availability">
            <h3 style="margin: 2px 0px 2px 0px;">Available</h3>
            <h4 style="margin: 2px 0px 2px 0px;">Inductees:</h4>
            <div id="available_inductees"></div>
            <h4 style="margin: 2px 0px 2px 0px;">Officers:</h4>
            <div id="available_officers"></div>
        </div>
        <div id="schedule"></div>
    </div>
</body>
</Layout>

<style>
    #slot_availability {
        display: flex;
        flex-direction: column;
        padding-left: 5px;
        margin-left: 50px;
        width: 15%;
        height: 100%;
        border: 1px solid black;
        border-radius: 5%;
    }
    #schedule {
        display: flex;
        flex-direction: row;
        padding-left: 10px;
        padding-bottom: 3vh;
        width: 80%;
        height: 100%;
    }
</style>