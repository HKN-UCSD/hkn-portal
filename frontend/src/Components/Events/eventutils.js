
async function reactToResponse(response) {
    let validResponseStatuses = [200, 201, 204];
    if (validResponseStatuses.some((stat) => response.status == stat)) {
        // const result = await response.json();
        // window.location.reload();
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
    form.set("anon_viewable", formData.eventToEdit.anon_viewable);

    for (const user of formData.eventToEdit.hosts) {
        form.append("hosts", user);
    }

    for (const group of formData.eventToEdit.view_groups) {
        form.append("view_groups", group);
    }

    return form;
}

export async function getAvailableSelfActions() {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let selfActions = availableActions.self_actions;
            return selfActions;
        } else {
            throw new Error(response.statusText);
        }
}


export async function getAvailableOtherActions() {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.other_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
}

/*
Add to calendar button by calling google calendar API
*/
export function addToCalendar(event) {
    let start_time = new Date(event.start_time);
    let end_time = new Date(event.end_time);
    let title = event.name;
    let location = event.location;
    let description = event.description;
    location = location.replace(/ /g, '+');
    let start = start_time.toISOString().replace(/-|:|\.\d+/g, '');
    let end = end_time.toISOString().replace(/-|:|\.\d+/g, '');
    let url = `https://www.google.com/calendar/render?action=TEMPLATE`+
    `&text=${title}&dates=${start}/${end}&details=${description}&location=${location}`;

    window.open(url, "_blank");

}

/**
 * Generates a console table that can be rendered in the event console.
 * This function is to only be called by users identifying as officers; other
 * users should receive empty arrays when the function tries to access the API.
 * The format of the table is:
 * 
 * @param {number} eventid The ID of the event to generate an object for
 * @returns Generates an object representing a console table that can be rendered
 * on event pages
 */
export async function fetchEventTable(event) {
    let rows = new Map();
    const eventid = event.pk;

    // obtain all information necessary for the action bar and console table.
    let actionRecords, relatedUsers, otherActions;
    [actionRecords, relatedUsers, otherActions] = await Promise.all([
        fetch(`/api/eventactionrecords/?eventid=${eventid}`).then((value) =>
            value.json(),
        ),
        fetch(`/api/users/?eventid=${eventid}`).then((value) =>
            value.json(),
        ),
        getAvailableOtherActions(),
    ]);


    // For each action record, update/create rows describing user activity
    actionRecords.forEach((actionRecord) => {
        const userId = actionRecord["acted_on"];
        let row = rows.get(userId);
        if (!row) {
            row = { Points: 0 };
            rows.set(userId, row);
        }
        row[actionRecord["action"] + " Time"] = new Date(
            actionRecord["action_time"],
        ).toLocaleString();
        // storing a record's id is necessary for deleting action records
        // as well as for deciding whether to produce an undo version of
        // this action
        row[actionRecord["action"] + " Id"] = actionRecord["pk"]; 
        row["Points"] += actionRecord["points"];
    });


    // for each user, update its relevant row with email and name
    relatedUsers.forEach((user) => {
        const userId = user["user_id"];
        const row = rows.get(userId);
        if (row) {
            row["Name"] = `${user["preferred_name"]} ${user["last_name"]}`;
            row["Email"] = user["email"];
            row["Id"] = user["user_id"];
        }
    });
    

    // for each row, add otherAction buttons (Not RSVP or Sign In)
    rows.forEach((row) => {
        otherActions.forEach((actionName) => {
            if (row[actionName + " Time"] == undefined) {
                row[actionName] = {
                    // TODO: Make requestAction just take the event id instead of
                    // a whole event object. It's sooo uglyyy rn
                    onclick: requestAction,
                    text: actionName,
                    args: [
                        event,
                        actionName,
                        { user_id: row["Id"] },
                    ],
                };
            } else {
                row[actionName] = {
                    onclick: deleteAction,
                    text: "un-" + actionName,
                    args: [row[actionName + " Id"]],
                };
            }
        });
    });
    return rows;
}
/*
Generate QR code by calling a QR Code API
*/
export function generateQRCode(event) {
    let url = `https://api.qrserver.com/v1/create-qr-code/?data=portal.hknucsd.com/events/${event.pk}?size=500x500`;
    window.open(url, "_blank");
}
