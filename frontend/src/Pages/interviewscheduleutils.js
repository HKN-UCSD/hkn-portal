// No way to remove date, so just set to 1970 Jan 1 8AM
const START_TIME = new Date(1970, 0, 1, 8, 0);

/* --- STYLES --- */
export const UNAVAILABLE_COLOR = "rgba(234, 166, 62, 0.4)";
export const AVAILABLE_COLOR = "rgba(92, 185, 240)";
export const SELECTED_COLOR = "rgba(35, 24, 244)";

// For each column in schedule
const DAY_COL = "display: flex; flex-direction: column;";

// For time labels column heading slot
const EMPTY_HEADING = "width: 4vw; height: max(3vh, 18px); margin: 0px 10px 3px 5px; text-align: center; "
// For slots in time labels column
const TIME_LABEL = "width: max(4vw, 50px); height: max(2vh, 15px); margin: 0px 5px 0px 0px; text-align: right;"

// For column headings
const COLUMN_HEADING = "width: 5vw; height: max(3vh, 18px); margin: 0px 5px 3px 5px; text-align: center; "
// For each timeslot in schedule
const TIMESLOT = `width: 5vw; height: max(2vh - 2px, 13px); border: 1px solid black; background: ${UNAVAILABLE_COLOR};`;

export const NUM_DAYS = 7;
export const NUM_SLOTS = 48;


/*
 * Generate the schedule table
 * Requires a div with id 'schedule' in the HTML file
 */
export function generateSchedule() {
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
    for (let slot = 0; slot < NUM_SLOTS; slot++) {
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
                label.innerText = time.getHours() + "AM";
            } else if (time.getHours() == 12) {
                label.innerText = "12PM";
            } else {
                label.innerText = time.getHours() - 12 + "PM";
            }
            label_col.appendChild(label);
        } else {
            empty_slot = document.createElement('div');
            empty_slot.style = TIME_LABEL;
            label_col.appendChild(empty_slot);
        }
    }

    // Create columns for each day
    for (let day = 0; day < NUM_DAYS; day++) {
        // Create column for the day
        let dayCol = document.createElement('div');
        dayCol.classList.add('dayCol');
        dayCol.style = DAY_COL;
        schedule.appendChild(dayCol);

        // Create column heading
        let colHeading = document.createElement('div');
        colHeading.style = COLUMN_HEADING;
        colHeading.innerText = dayNames[day];
        dayCol.appendChild(colHeading);

        // Generate timeslots in the day
        for (let slotNum = 0; slotNum < NUM_SLOTS; slotNum++) {
            // Create timeslot
            let timeslot = document.createElement('div');
            timeslot.id = day + '-' + slotNum;
            timeslot.classList.add('timeslot');
            timeslot.setAttribute('available', false);
            timeslot.style = TIMESLOT;
            let mod4 = slotNum % 4;
            switch (mod4) {
                case 0:
                    timeslot.style.borderTop = `1px solid ${SELECTED_COLOR}`;
                    timeslot.style.borderBottom = `1px dotted black`;
                    break;
                case 1:
                    timeslot.style.borderTop = `1px dotted black`;
                    timeslot.style.borderBottom = `1px dotted black`;
                    break;
                case 2:
                    timeslot.style.borderTop = `1px dotted black`;
                    timeslot.style.borderBottom = `1px dotted black`;
                    break;
                case 3:
                    timeslot.style.borderTop = `1px dotted black`;
                    timeslot.style.borderBottom = `1px solid black`;
                    break;
            }
            dayCol.appendChild(timeslot);
        }
    }
}