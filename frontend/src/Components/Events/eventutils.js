async function reactToResponse(response) {
    let validResponseStatuses = [200, 201, 204];
    if (validResponseStatuses.some((stat) => response.status == stat)) {
        // const result = await response.json();
        window.location.reload();
    } else {
        const message = await response.json();
        alert(`${response.statusText}: ${message['detail']}`);
    }
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
    await reactToResponse(response);
}

export async function deleteAction(actionId) {
    let getJSON = (response) => response.json();
    // Grab record and remove from assigned rides if needed
    // JSON of assigned rides is under "rides" column of "event" table
    const actionRecord = await fetch(`/api/eventactionrecords/${actionId}/`).then(getJSON);
    const user_id = actionRecord.user;
    const user = await fetch(`/api/users/${user_id}/`).then(getJSON);
    const event_id = actionRecord.event;
    const event = await fetch(`/api/events/${event_id}/`).then(getJSON);
    for (const key in event.rides) {
        let driver = event.rides[key]["driver"];
        if (driver == user.email) {
            event.rides[key]["driver"] = null;
        }
        let passengers = event.rides[key]["passengers"];
        console.log(passengers);
        for (const passenger of passengers) {
            const index = passengers.indexOf(passenger);
            passengers.splice(index, index);
        }
    }

    // now make an api call to `/api/events/${id}/` with method PUT
    // Must include name, start_time, end_time, and rides
    const formData = await populateFormToUpdateRides(event_id, JSON.stringify(event.rides));

    const CSRFToken = document.cookie
            .split("; ")
            .find((element) => element.startsWith("csrftoken="))
            .split("=")[1];
    formData.set("csrfmiddlewaretoken", CSRFToken);

    console.log(event_id);
    const eventResponse = await fetch(`/api/events/${event_id}/`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': CSRFToken,
        },
        body: new URLSearchParams(formData),
    });
    if (!eventResponse.ok) {
        alert(`Unable to save changes to event. Response status ${eventResponse.status}`);
    }

    // Delete RSVP Action
    const eventActionResponse = await fetch(`/api/eventactionrecords/${actionId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": document.cookie
                .split("; ")
                .find((element) => element.startsWith("csrftoken="))
                .split("=")[1],
        }
    });
    await reactToResponse(eventActionResponse);
}

export async function getFormData(idOfEventToEdit) {
    let getJSON = (response) => response.json();
    let [eventTypes, groups, officers] = await Promise.all([
        fetch("/api/eventtypes/").then(getJSON),
        fetch("/api/groups/").then(getJSON),
        fetch("/api/officers/").then(getJSON),
    ]);

    let formData = {
        eventTypes: eventTypes,
        groups: groups,
        officers: officers,
    };

    if (idOfEventToEdit != undefined) {
        // fetch event we want to edit and add it to formData, which is 
        // the information used to build the form.
        formData["eventToEdit"] = await fetch(
            `/api/events/${idOfEventToEdit}/`
        ).then(getJSON);
        let start_time_str = formData["eventToEdit"].start_time;
        let end_time_str = formData["eventToEdit"].end_time;

        // str is currently in GMT/UTC. Transform it into local time.
        // Annoyingly, the vanilla Date API only prints ISO format in UTC
        // time, so we'll produce a shifted UTC time instead of using an
        // equivalent locale datetime.
        // If we end up needing a lot of time manipulation, consider moment.js
        let currentStartDate = new Date(start_time_str);
        let currentEndDate = new Date(end_time_str);
        let shiftedStartDate = new Date(currentStartDate.getTime() - currentStartDate.getTimezoneOffset() * 60000);
        let shiftedEndDate = new Date(currentEndDate.getTime() - currentEndDate.getTimezoneOffset() * 60000);

        // HTML form default values require us to omit the 
        // seconds/milliseconds from ISO 8601 format. 
        let str = shiftedStartDate.toISOString();
        formData["eventToEdit"].start_time = str.substring(
            0,
            str.lastIndexOf(":")
        );
        str = shiftedEndDate.toISOString();
        formData["eventToEdit"].end_time = str.substring(
            0,
            str.lastIndexOf(":")
        );
    } else {
        formData["eventToEdit"] = {};
    }

    return formData;
}

// Populate form data to be sent to /api/events/event_id/ to update event
// Parameters: Rides (Stringified JSON)
// Output: form (new FormData object with required fields filled in)
export async function populateFormToUpdateRides(event_id, rides) {
    const formData = await getFormData(event_id);
    let form = new FormData();

    const start_date_in_utc = new Date(
        formData.eventToEdit.start_time
    ).toISOString();
    const end_date_in_utc = new Date(
        formData.eventToEdit.end_time
    ).toISOString();

    if (start_date_in_utc >= end_date_in_utc) {
        alert(`Start Time needs to be before End Time`);
        return false;
    }

    form.set("start_time", start_date_in_utc);
    form.set("end_time", end_date_in_utc);

    form.append("rides", rides);
    form.append("name", formData.eventToEdit.name);
    form.append("groups", formData.groups);

    for (const user of formData.eventToEdit.hosts) {
        form.append("hosts", user);
    }

    for (const group of formData.eventToEdit.view_groups) {
        form.append("view_groups", group);
    }

    return form;
}