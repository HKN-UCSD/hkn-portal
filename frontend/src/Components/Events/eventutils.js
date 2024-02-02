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
    console.log(action === "Check Off" ? event.points : 0);
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
    const response = await fetch(`/api/eventactionrecords/${actionId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": document.cookie
                .split("; ")
                .find((element) => element.startsWith("csrftoken="))
                .split("=")[1],
        }
    })
    await reactToResponse(response);
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
