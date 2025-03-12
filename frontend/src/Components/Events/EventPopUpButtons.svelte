<script>
    import "./eventutils";
    import { onMount } from "svelte";
    import {
        requestAction,
        deleteAction,
        getAvailableSelfActions,
        addToCalendar,
        generateQRCode,
    } from "./eventutils";
    // Buttons for RSVP and Sign In
    let selfActions = [];
    let isAdmin = false;
    let isPageLoading = true;
    let user = {};
    export let event;
    let eventid = event.pk
    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then((value) =>
            value.json(),
        );
        return response.is_admin;
    }
        // obtain user data
    async function getSelfUser(event) {
        let response = await fetch(`/api/users/self/`);
        if (response.status === 200) {
            let user = await response.json();
            let userRecordResponse = await fetch(
                `/api/eventactionrecords/pair/${event}/${user.user_id}/`,
            );
            let userRecord = await userRecordResponse.json();
            user["records"] = userRecord;
            return user;
        } else {
            throw new Error(response.statusText);
        }
    }

    const fetchAllEventData = async () => {
        try {
            // Call your asynchronous function that returns a promise
            user = await getSelfUser(eventid);
            isAdmin = await checkAdmin();
            selfActions = await getAvailableSelfActions(eventid);
            console.log("selfActions:", selfActions);
            isPageLoading = false;
        } catch (error) {
            console.error("Error fetching table data:", error);
        }
    }

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    onMount(() => {
        fetchAllEventData();
    });
</script>

<div class="flex gap-4 p-4 rounded-lg items-center justify-center">
    {#each selfActions as selfAction}
        {@const record = user.records.find((record) => record.action === selfAction)}
        {#if record == undefined}
            <button class="bg-primary text-white px-4 py-2 rounded hover:bg-secondary hover:text-white"
                on:click={() => requestAction(event, selfAction, user).then(fetchAllEventData)}>
                {selfAction}
            </button>
        {:else}
            <button class="bg-primary text-white px-4 py-2 rounded hover:bg-secondary hover:text-white"
                on:click={() => deleteAction(record.pk).then(fetchAllEventData)}>
                un{selfAction}
            </button>
        {/if}
    {/each}

    {#await checkAdmin()}
        <p>Loading... </p>
    {:then isAdmin}
        {#if isAdmin}
            <button class="bg-primary text-white px-4 py-2 rounded"
                on:click={() => generateQRCode(event)}>
                Generate QR Code
            </button>
        {/if}
    {/await}
</div>