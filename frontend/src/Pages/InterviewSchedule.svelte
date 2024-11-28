<!-- File for displaying overall interview schedule -->
<script>
    import Layout from "../Layout.svelte";
</script>
<svelte:head>
    <title> HKN Portal | Profile </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
<body onload="populateSchedule()">
    <script>
        // No way to remove date, so just set to 1970 Jan 1 8AM
        const START_TIME = new Date(1970, 0, 1, 8, 0);

        /* --- STYLES --- */
        // For each column in schedule
        const DAY_COL_STYLE = "display: flex; flex-direction: column;";
        
        // For time labels column heading slot
        const EMPTY_HEADING = "width: 4vw; height: max(3vh, 18px); margin: 0px 5px 3px 5px; text-align: center; "
        // For slots in time labels column
        const TIME_LABEL = "width: 4vw; height: max(2vh, 15px); margin: 0px 5px 0px 0px; text-align: right;"
        
        // For column headings
        const COLUMN_HEADING = "width: 5vw; height: max(3vh, 18px); margin: 0px 5px 3px 5px; text-align: center; "
        // For each timeslot in schedule
        const TIMESLOT_STYLE = "width: 5vw; height: max(2vh - 2px, 13px); border: 1px solid black;";

        const UNAVAILABLE_COLOR = "rgba(255, 255, 255)";
        const AVAILABLE_COLOR = "rgba(92, 185, 240)";
        const SELECTED_COLOR = "rgba(35, 24, 244)";

        let availabilities;
        async function getAvailabilities() {
            availabilities = await fetch(`api/inductionclasses/all_availabilities/`);
        }

        // Keep track of timeslot that was clicked
        let selected_slot = null;

        // Add event listener to document to manage clicks on timeslots
        document.addEventListener('click', function(event) {
            // No previously selected slot
            if (selected_slot == null) {
                if (event.target.classList.contains('timeslot')) {
                    selected_slot = event.target.id;
                    event.target.style.background = SELECTED_COLOR;
                    return;
                }
            } else {
                // Clicked on same slot, no change
                if (event.target.id == selected_slot) {
                    return;
                }
                let timeslot = document.getElementById(selected_slot);
                // Clicked on another slot
                if (event.target.classList.contains('timeslot')) {
                    selected_slot = event.target.id;
                    timeslot.style.background = AVAILABLE_COLOR;
                    event.target.style.background = SELECTED_COLOR;
                    return;
                }
                // Clicked elsewhere
                timeslot.style.background = AVAILABLE_COLOR;
                selected_slot = null;
                clearAvailabilityDisplay();
                return;
            }
        });

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

        availabilities = [
            [ // Sunday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Monday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Tuesday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Wednesday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Thursday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Friday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
            [ // Saturday
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
                {"inductees": ["Alice Smith", "Bob Johnson"], "officers": ["John Doe", "Jane Roe"]},
            ],
        ];

        async function populateSchedule() {
            let dayNames = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
            let schedule = document.getElementById('schedule');

            // Create first column for time labels and add to schedule
            let label_col = document.createElement('div');
            schedule.appendChild(label_col);

            // Insert empty slot for formatting
            let empty_slot = document.createElement('div');
            empty_slot.style = EMPTY_HEADING;
            label_col.appendChild(empty_slot);

            // Populate time labels
            for (let slot = 0; slot < availabilities[0].length; slot++) {
                let time = new Date(START_TIME.getYear(),
                                    START_TIME.getMonth(),
                                    START_TIME.getDate(),
                                    START_TIME.getHours(), 
                                    START_TIME.getMinutes() + (slot * 15)
                                );

                // create label for full hours
                if (time.getMinutes() == 0) {
                    let label = document.createElement('div');
                    label.style = TIME_LABEL;
                    // Use AM and PM
                    if (time.getHours() < 12) {
                        label.innerText = time.getHours() + " AM";
                    } else {
                        label.innerText = time.getHours() + " PM";
                    }
                    label_col.appendChild(label);
                } else {
                    empty_slot = document.createElement('div');
                    empty_slot.style = TIME_LABEL;
                    label_col.appendChild(empty_slot);
                }
            }

            // Create columns for each day
            for (let day = 0; day < availabilities.length; day++) {
                // Create column for the day
                let dayCol = document.createElement('div');
                dayCol.classList.add('dayCol');
                dayCol.style = DAY_COL_STYLE;
                schedule.appendChild(dayCol);

                // Create column heading
                let colHeading = document.createElement('div');
                colHeading.style = COLUMN_HEADING;
                colHeading.innerText = dayNames[day];
                dayCol.appendChild(colHeading);

                // Generate timeslots in the day
                availabilities[day].forEach(timeslot => {
                    // Create timeslot
                    let time = document.createElement('div');
                    time.id = day + '-' + availabilities[day].indexOf(timeslot);
                    time.classList.add('timeslot');
                    time.style = TIMESLOT_STYLE;
                    // Populate timeslots
                    if (timeslot['inductees'].length != 0) {
                        // make timeslot colored
                        time.style.background = AVAILABLE_COLOR;
                    }
                    // Add event listener to check for mouseover to display inductees and officers
                    time.addEventListener('mouseover', function() {
                        const P_STYLE = "margin: 1px 0px 1px 0px;";
                        if (selected_slot != null) {
                            return;
                        }
                        clearAvailabilityDisplay();
                        let inductees = timeslot['inductees'];
                        let available_inductees = document.getElementById('available_inductees');
                        inductees.forEach(inductee => {
                            let name = document.createElement('p');
                            name.innerText = inductee;
                            name.style = P_STYLE;
                            available_inductees.appendChild(name);
                        });

                        let officers = timeslot['officers'];
                        let available_officers = document.getElementById('available_officers');
                        officers.forEach(officer => {
                            let name = document.createElement('p');
                            name.innerText = officer;
                            name.style = P_STYLE;
                            available_officers.appendChild(name);
                        })
                    });
                    time.addEventListener('mouseout', function() {
                        if (selected_slot != null) {
                            return;
                        }
                        clearAvailabilityDisplay();
                    });
                    dayCol.appendChild(time);
                });
            }
        }
    </script>
    <div style="padding-left:50px">
        <h1>Interview Availabilities</h1>
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
        border-radius: 15%;
    }
    #schedule {
        display: flex;
        flex-direction: row;
        padding-left: 10px;
        width: 80%;
        height: 100%;
    }
</style>