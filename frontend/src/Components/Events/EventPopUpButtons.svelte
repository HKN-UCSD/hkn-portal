<script>
    import "./eventutils";
    import { onMount } from "svelte";
    import {
        requestAction,
        deleteAction,
        getAvailableSelfActions,
        generateQRCode,
    } from "./eventutils";
    // Buttons for RSVP and Sign In
    let selfActions = [];
    let isAdmin = false;
    let isPageLoading = true;
    let user = {};
    export let event;
    let eventid = event.pk
    let errorActions = [];
    let errorImagePath = '/static/miscellaneous/meow.jpg'; 
    let errorSoundPath = '/static/miscellaneous/meow.mp3'
    const audio = new Audio(errorSoundPath);
    audio.load();

    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then((value) =>
            value.json(),
        );
        return response.is_admin;
    }

    function playErrorSound() {
    
        audio.play().catch((e) => {
            console.warn("Autoplay failed:", e);
        }); 
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

    async function handleRequestAction(event, selfAction, user) {
        try {
            await requestAction(event, selfAction, user);
        } catch (err) {
            console.error(`Error on ${selfAction}:`, err);
            playErrorSound();
            if (!errorActions.includes(selfAction)) {
                errorActions = [...errorActions, selfAction];
            }
            // Remove after 1 second
            setTimeout(() => {
                errorActions = errorActions.filter(action => action !== selfAction);
            }, 400);
        } finally {
            fetchAllEventData();
        }
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
                on:click={() => handleRequestAction(event, selfAction, user).then(fetchAllEventData)}>
                {selfAction}
            </button>
        {:else}
            <button class="bg-primary text-white px-4 py-2 rounded hover:bg-secondary hover:text-white"
                on:click={() => deleteAction(record.pk).then(fetchAllEventData)}>
                un{selfAction}
            </button>
        {/if}

        {#if errorActions.includes(selfAction)}
            <img
                src = {errorImagePath}
                alt = "error"
                class="absolute top-0 left-0 w-full h-full object-cover z-10 rounded"
            />
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