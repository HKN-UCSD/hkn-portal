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
</script>

<svelte:head>
    <title> HKN Portal | Event Details </title>
</svelte:head>

<main>
    <div>
        {#await getEvent(id)}
            <p>Loading...</p>
        {:then selectedEvent}
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
                        }}>Edit</button
                    >
                    <h3>Danger Zone</h3>
                    <button class="danger" on:click={onDelete}>Delete</button>
                {/if}
            {:catch error}
                <p>Error: {error.message}</p>
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