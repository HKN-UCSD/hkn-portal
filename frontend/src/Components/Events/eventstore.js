import { writable } from 'svelte/store'

export const eventstore = writable();
export const eventview = writable("list");


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

export async function requestAction(event, action, userActedOn) {
    const response = await fetch(`/api/eventactionrecords/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.cookie
                .split("; ")
                .find((element) => element.startsWith("csrftoken="))
                .split("=")[1],
        },
        body: JSON.stringify({
            event: event.pk,
            acted_on: userActedOn.user_id,
            action: action,
            extra_data: "{}",
            points: action === "Check Off" ? event.points: 0,
        }),
    });
    const result = await response.json();
    console.log(result);
    window.location.reload();
}
