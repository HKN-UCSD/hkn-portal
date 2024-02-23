<script>
    import { getEvent } from "../../Components/Events/eventstore";
    import EventDetailContent from "../../Components/Events/EventDetailContent.svelte";
    import { navigate } from "svelte-routing";
    export let id;

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    async function onReady() {
        try {
            const response = await fetch(`/api/events/${id}/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.cookie
                        .split("; ")
                        .find((element) => element.startsWith("csrftoken="))
                        .split("=")[1],
                },
                body: JSON.stringify({
                    is_draft: false,
                }),
            });

            if (!response.ok) {
                alert(
                    `Unable to ready event. Response status ${response.status}`
                );
            } else {
                alert("Successfully marked the event as ready");
                navigate("/");
            }
        } catch (error) {
            alert(`Unable to ready event. API error ${error}`);
        }
    }

    async function onDelete() {
        const isConfirmed = window.confirm("Are you sure you want to delete this event?");
        if (isConfirmed) {
            try {
                const response = await fetch(`/api/events/${id}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.cookie
                            .split("; ")
                            .find((element) => element.startsWith("csrftoken="))
                            .split("=")[1],
                    },
                });

                if (!response.ok) {
                    alert(
                        `Unable to delete event. Response status ${response.status}`
                    );
                } else {
                    alert("Successfully deleted event");
                    navigate("/");
                }
            } catch (error) {
                alert(`Unable to delete event. API error ${error}`);
            }
        }
    }

    async function checkRides(event) {
        // No need to check if not outreach event
        if (event.event_type != "Outreach") {
            return;
        }

        // Do not check if user is not officer
        let permission = await (await fetch(`/api/permissions/`)).json();
        if (!permission.is_admin) {
            return;
        }

        // Do not check if user is not host
        let user = await (await fetch(`/api/profile/self/`)).json();
        if (!event.hosts.find(host => host == user.user_id)) {
            return;
        }

        function parseEmail(attendee) {
            return attendee.split("(")[1].split(")")[0];
        }

        const users = await (await fetch(`/api/users/`)).json();
        const actionRecords = await (await fetch(`/api/eventactionrecords/`)).json();
        const rsvpRecords = actionRecords.filter(record => {
            return record.action == 'RSVP' && record.event == event.pk;
        });
        const rides = event.rides;
        let unRSVP = [];

        for (const key in rides) {
            if (rides[key]["driver"]) {
                const driverEmail = parseEmail(rides[key]["driver"])
                const driver = users.find(user => user.email == driverEmail);
                if (!rsvpRecords.find(record => record.acted_on == driver.user_id)) {
                    unRSVP.push(rides[key]["driver"]);
                }
            }
            for (const attendee of rides[key]["passengers"]) {
                const passengerEmail = parseEmail(attendee);
                const passenger = users.find(user => user.email == passengerEmail);
                if (!rsvpRecords.find(record => record.acted_on == passenger.user_id)) {
                    unRSVP.push(attendee);
                }
            }
        }

        if (unRSVP.length != 0) {
            let alertMessage = 'The following attendees with assigned rides have un-RSVP\'d:\n';
            for (const user of unRSVP) {
                alertMessage += user + '\n';
            }
            alert(alertMessage);
        }
    }

    async function isHost(event) {
        const user = await (await fetch(`/api/profile/self/`)).json();
        if (event.hosts.find(host => host == user.user_id)) {
            return true;
        }
        return false;
    }
</script>

<svelte:head>
    <title> HKN Portal | Event Details </title>
</svelte:head>

<main>
    <div>
        {#await getEvent(id)}
            <p>Loading...</p>
        {:then selectedEvent}
            {#await checkRides(selectedEvent)}
                <p>Loading...</p>
            {:then}
                <EventDetailContent {selectedEvent} />
                <br />
                {#await getPermissions()}
                    <p>Loading...</p>
                {:then permissions}
                    {#if permissions.is_admin}
                        {#if selectedEvent.is_draft}
                            <button on:click={onReady}>Ready</button>
                        {/if}
                        <button
                            on:click={() => {
                                navigate(`/events/edit/${id}`);
                            }}>Edit
                        </button>
                        {#if selectedEvent.event_type == "Outreach"}
                            {#await isHost(selectedEvent)}
                                <p>Loading...</p>
                            {:then isHost}
                                {#if isHost}
                                    <button
                                        on:click={() => {
                                            navigate(`/events/rides/${id}`);
                                        }}>Assign Rides
                                    </button>
                                {/if}
                            {/await}
                        {/if}
                        <h3>Danger Zone</h3>
                        <button class="danger" on:click={onDelete}>Delete</button>
                    {/if}
                {:catch error}
                    <p>Error: {error.message}</p>
                {/await}
            {/await}
        {:catch error}
            <p>Error: {error.message}</p>
        {/await}
    </div>
</main>

<style>
    div {
        padding: 30px;
        padding-top: 10px;
        margin: 30px;
    }

    .danger {
        background-color: indianred;
    }

    /* Quick band-aid for button spacing */
    button {
        margin: 5px;
    }
</style>