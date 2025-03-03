<!-- File for page displaying overall interview schedule -->
<script>
    import Layout from "../Layout.svelte";
    import { onMount } from "svelte";
    import { days, timeslots, UNAVAILABLE_COLOR, MAX_GRADIENT_COLOR, SELECTED_COLOR } from "./interviewscheduleutils.js"

    let availabilities;
    let inductee_availabilities = {};
    let inductees;
    let selected_slot = null;
    let loaded = false;
    let inductee_slot_colors = [UNAVAILABLE_COLOR];

    onMount(async () => {
        // Retrieve availabilities of all inductees and officers from backend
        await getAvailabilities();
        await getInducteeAvailabilities();

        // Populate the schedule according to availabilities retrieved
        if (availabilities != null) {
            setColorsInductees();
            populateSchedule();
        }

        /*
         * Add event listener to document to manage clicks on timeslots
         * If a timeslot is clicked, lock 'avaiilability' display to that timeslot
         */
        document.addEventListener('click', (event) => {
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
                        if (inductee_option[0] == 'all') {
                            timeslot.style.background = inductee_slot_colors[availabilities[day][slot]['inductees'].length]
                        } else if (inductee_availabilities[inductee_option[0]][day][slot] == 1) {
                            let officer_slot_colors = setColorsOfficers(inductee_availabilities[inductee_option[0]]);
                            timeslot.style.background = officer_slot_colors[availabilities[day][slot]['officers'].length];
                        } else {
                            timeslot.removeAttribute('style');
                        }
                    } catch {
                        timeslot.removeAttribute('style');
                    }
                    setAvailabilityDisplay(event.target.id);
                } else if (event.target.classList.contains('timeslot')) {
                    // Clicked on another slot
                    selected_slot = event.target.id;
                    // Reset previously selected slot
                    try {
                        if (inductee_option[0] == 'all') {
                            timeslot.style.background = inductee_slot_colors[availabilities[day][slot]['inductees'].length]
                        } else if (inductee_availabilities[inductee_option[0]][day][slot] == 1) {
                            let officer_slot_colors = setColorsOfficers(inductee_availabilities[inductee_option[0]]);
                            timeslot.style.background = officer_slot_colors[availabilities[day][slot]['officers'].length];
                        } else {
                            timeslot.removeAttribute('style');
                        }
                    } catch {
                        timeslot.removeAttribute('style');
                    }
                    event.target.style.background = SELECTED_COLOR;
                    setAvailabilityDisplay(event.target.id);
                } else {
                    // Clicked elsewhere
                    try {
                        if (inductee_option[0] == 'all') {
                            timeslot.style.background = inductee_slot_colors[availabilities[day][slot]['inductees'].length]
                        } else if (inductee_availabilities[inductee_option[0]][day][slot] == 1) {
                            let officer_slot_colors = setColorsOfficers(inductee_availabilities[inductee_option[0]]);
                            timeslot.style.background = officer_slot_colors[availabilities[day][slot]['officers'].length];
                        } else {
                            timeslot.removeAttribute('style');
                        }
                    } catch {
                        timeslot.removeAttribute('style');
                    }
                    selected_slot = null;
                    clearAvailabilityDisplay();
                }
            }
        });
    });

    /*
     * Make an api call to the backend to retrieve all availabilities
     * Format of availabilities: 2D array availabilities[day][slot] = {inductees: [full names], officers: [full names]}
     */
    async function getAvailabilities() {
        const response = await fetch(`api/inductionclasses/all_availabilities/`);
        if (response.ok) {
            availabilities = await response.json();
        } else {
            availabilities = null;
        }
    }

    /**
     * Make an api call to the backend to retrieve all inductee availabilities
     * Format of inductee_availabilities: dictionary of user_id: availability
     */
    async function getInducteeAvailabilities() {
        const response = await fetch(`api/inductionclasses/inductee_availabilities/`);
        let list;
        if (response.ok) {
            list = await response.json();
        } else {
            list = null;
        }
        
        if (list != null) {
            inductees = [];
            for (let user_id in list) {
                inductees.push([user_id, list[user_id][0]]);
                inductee_availabilities[user_id] = list[user_id][1];
            }
            inductees.sort((a, b) => a[1].localeCompare(b[1], undefined, {sensitivity: 'base'}));
        } else {
            inductee_availabilities = null;
        }
    }
  
    /*
     * Sets the availability display to show the inductees and officers available at the selected timeslot
     */
    function setAvailabilityDisplay(id) {
        let day = id.split('-')[0];
        let slot = id.split('-')[1];

        clearAvailabilityDisplay();
        let inductees_filtered;
        let officers;
        try {
            inductees_filtered = availabilities[day][slot]['inductees'].filter(inductee => inductee == inductee_option[1] || inductee_option[0] == "all");
            officers = availabilities[day][slot]['officers'];
        } catch {
            return;
        }
        
        let available_inductees = document.getElementById('available_inductees');
        let available_officers = document.getElementById('available_officers');

        const P_STYLE = "margin: 1px 0px 1px 0px;";
        inductees_filtered.forEach(inductee => {
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

    /*
     * Clear the availability display
     */
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
     * Find max number of inductees in an individual timeslot and prepare color gradients accordingly.
     */
    function setColorsInductees() {
        let max = 0;
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                if (availabilities[day][slotNum]['inductees'].length > max) {
                    max = availabilities[day][slotNum]['inductees'].length;
                }
            }
        }

        let avail_color = MAX_GRADIENT_COLOR.split(",");
        let r = avail_color[0].split("(")[1];
        let g = avail_color[1];
        let b = avail_color[2].split(")")[0];

        // Base color = rgba(95, 192, 249) light blue
        let step_r = (255 - r) / (max + 2);
        let step_g = (255 - g) / (max + 2);
        let step_b = (255 - b) / (max + 2);
        
        for (let i = 0; i < max; i++) {
            // TODO: populate inductee_slot_colors with a giadient from starting color to ending color.
            // Also need to change color of selected timeslot.
            let color = `rgba(${255 - step_r * (i + 2)}, ${255 - step_g * (i + 2)}, ${255 - step_b * (i + 2)})`;
            inductee_slot_colors.push(color);
        }
    }

    /*
     * Find max number of officers in an individual timeslot (only consider ones that are marked available for this inductee)
     * and prepare color gradients accordingly.
     */
    function setColorsOfficers(inductee_availability) {
        let officer_slot_colors = [UNAVAILABLE_COLOR];
        let max = 0;
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                if ((inductee_availability[day][slotNum] == 1) && (availabilities[day][slotNum]['officers'].length > max)) {
                    max = availabilities[day][slotNum]['officers'].length;
                }
            }
        }

        let avail_color = MAX_GRADIENT_COLOR.split(",");
        let r = avail_color[0].split("(")[1];
        let g = avail_color[1];
        let b = avail_color[2].split(")")[0];

        // Base color = rgba(95, 192, 249) light blue
        let step_r = (255 - r) / (max + 2);
        let step_g = (255 - g) / (max + 2);
        let step_b = (255 - b) / (max + 2);

        for (let i = 0; i < max; i++) {
            // TODO: populate inductee_slot_colors with a giadient from starting color to ending color.
            // Also need to change color of selected timeslot.
            let color = `rgba(${255 - step_r * (i + 2)}, ${255 - step_g * (i + 2)}, ${255 - step_b * (i + 2)})`;
            officer_slot_colors.push(color);
        }
        return officer_slot_colors;
    }

    /*
     * Populate the schedule with availabilities
     * Attach mouseover and mouseout events on slots with availabilties
     * Mouseover event displays inductees and officers available at that timeslot in the availability display
     */
    function populateSchedule() {
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);

                // Make timeslot colored accordingly
                let numInductees = availabilities[day][slotNum]['inductees'].length;
                timeslot.style.background = inductee_slot_colors[numInductees];
                if (numInductees == 0) {
                    timeslot.setAttribute['available', false];
                } else {
                    timeslot.setAttribute['available', true];
                }

                // Add mouseover event listener to display inductees and officers at timeslot
                timeslot.addEventListener('mouseover', function() {
                    const P_STYLE = "margin: 1px 0px 1px 0px;";
                    if (selected_slot != null) {
                        return;
                    }
                    clearAvailabilityDisplay();

                    // Populate availability display with inductees available at that time
                    let inductees = availabilities[day][slotNum]['inductees'];
                    let available_inductees = document.getElementById('available_inductees');
                    inductees.forEach(inductee => {
                        let name = document.createElement('p');
                        name.innerText = inductee;
                        name.style = P_STYLE;
                        available_inductees.appendChild(name);
                    });

                    // Populate availability display with officers available at that time
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

    /*
     * Populate the schedule with individual inductee's availabilities
     * Attach mouseover and mouseout events on slots with availabilties
     * Mouseover event displays inductees and officers available at that timeslot in the availability display
     * Set on click event to only display the selected inductee
     */
     function populateInducteeSchedule(inductee_availability) {
        let officer_slot_colors = setColorsOfficers(inductee_availability);
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);

                // Make timeslot colored if an inductee has availability at that time
                let numOfficers = availabilities[day][slotNum]['officers'].length;
                if (inductee_availability[day][slotNum] == 1) {
                    timeslot.style.background = officer_slot_colors[numOfficers];
                    timeslot.setAttribute('available', true);
                }

                // Add mouseover event listener to display inductees and officers at timeslot
                timeslot.addEventListener('mouseover', function() {
                    const P_STYLE = "margin: 1px 0px 1px 0px;";
                    if (selected_slot != null) {
                        return;
                    }
                    clearAvailabilityDisplay();

                    // Populate availability display with inductees available at that time
                    let inductees_filtered = availabilities[day][slotNum]['inductees'].filter(inductee => inductee == inductee_option[1]);
                    let available_inductees = document.getElementById('available_inductees');
                    inductees_filtered.forEach(inductee => {
                        let name = document.createElement('p');
                        name.innerText = inductee;
                        name.style = P_STYLE;
                        available_inductees.appendChild(name);
                    });

                    // Populate availability display with officers available at that time
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

    /**
     * Clear schedule
     */
    function clear_schedule() {
        for (let day = 0; day < days.length; day++) {
            for (let slotNum = 0; slotNum < timeslots.length; slotNum++) {
                let timeslot = document.getElementById(`${day}-${slotNum}`);
                timeslot.removeAttribute('style');
                timeslot.setAttribute('available', false);
            }
        }
    }


    let inductee_option;

    /*
     * Filter out the selected inductee's availabilities
     */
    function filter() {
        if (inductee_availabilities[inductee_option[0]] != null) {
            clear_schedule();
            populateInducteeSchedule(inductee_availabilities[inductee_option[0]]);
        } else {
            clear_schedule();
            populateSchedule();
        }
    }

    // Filter the data when schedule if loaded and any inductee is selected from dropdown
    $: {
        inductee_option;
        if (loaded && inductee_availabilities) filter();
        }
</script>

<svelte:head>
    <title> HKN Portal | Interview Schedule </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
<body>
    <div class="flex flex-col">
        <div class="relative">
            <h1 class="w-full text-center text-5xl font-bold mt-10 mb-6 p-3 animate-slide-up text-primary transition-transform duration-300 hover:scale-110">All Availabilities</h1>
        </div>
        <div class="flex flex-row mt-6 mb-6 justify-center items-start">
            <div class="flex flex-col gap-4">
                {#if inductees}
                    <select bind:value={inductee_option}
                            class="w-1/2 pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                    hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500
                                    transition-all cursor-pointer">
                        <option value={{0: "all"}}>Filter by Inductee</option>
                        {#each inductees as inductee}
                            <option value={inductee}>{inductee[1]}</option>
                        {/each}
                    </select>
                {:else}
                    <h1>Loading</h1>
                {/if}
                <!-- Schedule -->
                <div class="flex overflow-x-auto text-primary">
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
                </div>
            </div>

            <!-- Availability Display -->
            <div id="slot_availability" class="sticky top-20 flex flex-col ml-6 p-4 pt-1 border border-gray-300 rounded-xl text-primary shadow-md hover:shadow-xl transform transition-transform duration-300 ease-in-out">
                <h3 class="text-xl font-bold mt-2">Available</h3>
                <h4 class="mt-2">Inductees:</h4>
                <div id="available_inductees" class="mt-2"></div>
                <h4 class="mt-2">Officers:</h4>
                <div id="available_officers"></div>
            </div>
        </div>
    </div>
</body>
</Layout>