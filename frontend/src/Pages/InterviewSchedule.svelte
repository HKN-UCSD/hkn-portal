<!-- File for displaying overall interview schedule -->
<script>
    import { onMount } from "svelte";
    import Layout from "../Layout.svelte";
    // 2D array where each element arr[i][j] = json of {inductees: [names], officers: [names]}
    // i = day of week [0, 6]
    // j = time slot in day (time = 8:00AM + (j * 15 minutes))
    let availabilities;
    onMount(async () => {
        availabilities = await fetch(`api/allavailabilities/`)
    });

</script>
<svelte:head>
    <title> HKN Portal | Profile </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
<body onload="populateSchedule()">
    <script>
        // No way to remove date, so just set to 1970 Jan 1 8AM
        const UTC_START_TIME = new Date(Date.UTC(1970, 0, 1, 8, 0));
        let availabilities;
        async function getAvailabilities() {
            availabilities = await fetch(`api/allavailabilities/`);
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
            const START_TIME = 
            let schedule = document.getElementById('schedule');

            // Create first column for time labels and add to schedule
            let label_col = document.createElement('div');
            schedule.appendChild(label_col);

            // Populate time labels
            for (let slot = 0; slot < availabilities[0].length; slot++) {
                let time = START_TIME.add;
                // console.log(time.toString());
                // console.log(START_TIME.toString());
                // console.log(SLOT_SIZE.toString());
                if (time.getMinutes() == 0) {
                    // create label for full hours
                    let label = document.createElement('h3');
                    // Use AM and PM
                    if (time < 12) {
                        label.innerText = time.getHours() + " AM";
                    } else {
                        label.innerText = time.getHours() + " PM";
                    }
                    label_col.appendChild(label);
                } else {
                    label_col.appendChild(document.createElement('div'));
                }
            }

            // Create columns for each day
            for (let day = 0; day < availabilities.length; day++) {
                // create column for the day

                // create column heading and add to column
                const colHeading = document.createElement('h2');
                column.appendChild(colHeading);
                colHeading.innerText = dayNames[day];

                // generate timeslots in the day
                for (let timeslot in day) {
                    // create timeslot
                    const time = document.createElement('div');
                    time.classList.add('timeslot');
                    // populate timeslots
                    if (timeslot['inductees'].length != 0) {
                        // make timeslot colored
                    }
                    // add event listener to check for mouse hover and display inductees and officers
                }
            }
        }
    </script>
    <div style="padding-left:50px">
        <h1 style="margin-left: 15px">Interview Availabilities</h1>
    </div>
    <div>

    </div>
    <div id="schedule"></div>
    <!-- <div id="schedule">
        <div class="dayCol">
            <h2>SU</h2>
        </div>
        <div class="dayCol">
            <h2>MO</h2>
        </div>
        <div class="dayCol">
            <h2>TU</h2>
        </div>
        <div class="dayCol">
            <h2>WE</h2>
        </div>
        <div class="dayCol">
            <h2>TH</h2>
        </div>
        <div class="dayCol">
            <h2>FR</h2>
        </div>
        <div class="dayCol">
            <h2>SA</h2>
        </div>
    </div> -->
</body>
</Layout>

<style>
    #schedule {
        display: flex;
        flex-direction: row;
    }
    .dayCol {
        display: flex;
        flex-direction: column;
    }
    .timeslot {
        border: black;
        width: 50px;
        height: 10px;
    }
</style>