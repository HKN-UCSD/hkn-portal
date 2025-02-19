<script>
    import { onMount, onDestroy } from "svelte";
    import { requestAction, deleteAction } from "./eventutils";
    import EventCard from "./EventCard.svelte";

    export let title;
    export let subtitle;
    export let events = [];
    

    let userData = null;
    let RSVP = null;
    let displayedEvents = [];  // Stores currently visible events
    let batchSize = 9; // Number of events to load per batch
    let loadedCount = 0; // Number of events currently loaded

    async function getUserData() {
        try {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
                userData = await response.json();
                let userRecordResponse = await fetch(`/api/eventactionrecords/user/${userData.user_id}/`);
                let userRecord = await userRecordResponse.json();
                RSVP = userRecord.filter((record) => record.action == "RSVP");
            } else {
                console.error("Failed to fetch self data");
            }
        } catch (error) {
            console.error("Error fetching user data", error);
        }
    }

    async function toggleRSVP(event, e) {
        e.stopPropagation(); // Stop the event from bubbling up to the parent

        //check if the event is already RSVP'd
        if (RSVP.find((record) => record.event == event.pk)) {
        deleteAction(RSVP.find((record) => record.event == event.pk).pk);      } else {
        await requestAction(event, "RSVP",userData);
        }
        await getUserData();
    }

    onMount(async () => {
      // Fetch events from the server
        await getUserData();
        const curr = new Date().toISOString();
    });

</script>

<div class=" mx-5 bg-gray-50 md:mx-auto text-primary">
    <div class="border border-gray-300 rounded-lg shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out">
        <h1 class="text-3xl font-bold  mb-8">{title}</h1>
        {#if subtitle}
          <p class="text-gray-500">{subtitle}</p>
        {/if}
        {#if events.length == 0}
            <div class="flex flex-col md:flex-col max-h-[1000px] overflow-x-auto">
              <div class="flex flex-col items-center justify-center w-full h-full py-10">
                <p class="text-gray-600 text-lg font-semibold">No events available at the moment.</p>
                <p class="text-gray-500 text-sm mt-2">Please check back later.</p>
              </div>
            </div>
          {/if}

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 min-h-screen overflow-y-auto w-full">

            {#each events as event}
              <EventCard {event} {toggleRSVP} {RSVP}/>
            {/each}
          </div>
        </div>

  </div>

