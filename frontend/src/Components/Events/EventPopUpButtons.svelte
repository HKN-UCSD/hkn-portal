<script>
    let errorSoundPath = '/static/miscellaneous/meow.mp3';
    const audio = new Audio(errorSoundPath);
    audio.load();

    //Necessary because sound loads so slow
    import "./eventutils";
    import { toastMessage, showToast } from './toaststore';
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
    let errorImagePath = '/static/miscellaneous/meow.jpg'; 
    let showErrorImage = false;
    


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

    async function handleRequestAction(event, selfAction, user) {
        try {
            await requestAction(event, selfAction, user);
        } catch (err) {
            audio.play().catch((e) => {
                console.warn("Autoplay failed:", e);
            }); 
            showErrorImage = true; 
            setTimeout(() => {
                showErrorImage = false;
            }, 400);             
        } finally {
            fetchAllEventData();
        }
    }

    onMount(() => {
        fetchAllEventData();
    });


</script>

<div class="flex gap-4 p-4 rounded-lg justify-center">
    {#each selfActions as selfAction}
        {@const record = user.records.find((record) => record.action === selfAction)}
        {#if record == undefined}
            <button class="bg-primary text-white px-4 py-2 min-h-[3rem] rounded hover:bg-secondary"
                on:click={() => handleRequestAction(event, selfAction, user).then(fetchAllEventData)}>
                {selfAction}
            </button>
        {:else}
            <button class="bg-primary text-white px-4 py-2 min-h-[3rem] rounded hover:bg-secondary"
                on:click={() => deleteAction(record.pk).then(fetchAllEventData)}>
                un{selfAction}
            </button>
        {/if}
    {/each}


    {#await checkAdmin()}
        <p>Loading... </p>
    {:then isAdmin}
        {#if isAdmin}
            <button class="bg-primary text-white px-4 py-2 rounded min-h-[3rem] hover:bg-secondary"
                on:click={() => generateQRCode(event)}>
                Generate QR Code
            </button>
        {/if}
    {/await}
    
    {#if showErrorImage}
    <img
        src={errorImagePath}
        alt="error"
        class="fixed top-0 left-0 w-screen h-screen object-cover z-50 pointer-events-none"
    />
    {/if}
    {#if $showToast}
        <div class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-600 text-white px-4 py-2 rounded shadow-lg z-50">
            {$toastMessage}
            
        </div>
    {/if}
</div>