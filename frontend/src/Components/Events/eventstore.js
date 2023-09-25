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

export async function getEventActions() {
    let response = await fetch(`/api/eventactions/`);
    return await response.json();
}