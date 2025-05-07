// No way to remove date, so just set to 1970 Jan 1 8AM
const START_TIME = new Date(1970, 0, 1, 8, 0);

/* --- STYLES --- */
export const UNAVAILABLE_COLOR = "rgba(220, 220, 220)";
export const AVAILABLE_COLOR = "rgba(92, 185, 240)";
export const MAX_GRADIENT_COLOR = "rgba(0, 0, 255)";
export const SELECTED_COLOR = "rgba(218, 106, 107)";
export let days = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];
export let timeslots = [
    "8:00", "8:15", "8:30", "8:45",
    "9:00", "9:15", "9:30", "9:45",
    "10:00", "10:15", "10:30", "10:45",
    "11:00", "11:15", "11:30", "11:45",
    "12:00", "12:15", "12:30", "12:45",
    "13:00", "13:15", "13:30", "13:45",
    "14:00", "14:15", "14:30", "14:45",
    "15:00", "15:15", "15:30", "15:45",
    "16:00", "16:15", "16:30", "16:45",
    "17:00", "17:15", "17:30", "17:45",
    "18:00", "18:15", "18:30", "18:45",
    "19:00", "19:15", "19:30", "19:45",
];