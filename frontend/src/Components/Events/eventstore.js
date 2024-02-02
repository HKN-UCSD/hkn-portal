import { writable } from 'svelte/store'

export const eventstore = writable();
export const eventview = writable("list");

export const consoleLayoutStore = writable({
    filter: [], 
    sort: null,
    selectedProperties: [
        "Name",
        "Email",
        "RSVP Time",
    ],
});


export async function getEvents() {
    let response = await fetch("/api/events/");
    return await response.json();
};

export async function getEvent(id) {
    let response = await fetch(`/api/events/${id}/`);
    return await response.json();
};


export async function getEventActionButtons() {
        let response = await fetch("/api/interface/action-buttons/");
        return await response.text();
}

