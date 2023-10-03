import { writable } from 'svelte/store'

export const eventstore = writable();
export const eventview = writable("list");


export async function getEvents() {
    // TODO
    let response = await fetch("/api/events/");
    return await response.json();
};

export async function getEvent(id) {
    // TODO
    let response = await fetch(`/api/events/${id}/`);
    return await response.json();
};


export async function getEventActionButtons() {
        let response = await fetch("/api/interface/action-buttons/");
        return await response.text();
}

export async function getEventPermissions() {
    let response = await fetch(`/api/event_permissions/`);
    return await response.json();
};
