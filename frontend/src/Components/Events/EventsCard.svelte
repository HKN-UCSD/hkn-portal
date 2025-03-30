
<script>
    import { onMount } from "svelte";

    import {requestAction, deleteAction} from "./eventutils";
    import EventCard from "./EventCard.svelte";


    // Get passed in data
    export let title;
    export let subtitle;
    export let events;
    export let RSVPEnabled;
    export let handleEventClick;
    
    // Get user data
    let userData = null
    let RSVP = null


    async function getUserData() {
        try {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
                userData = await response.json();
                let userRecordResponse = await fetch(`/api/eventactionrecords/user/${userData.user_id}/`);
                let userRecord = await userRecordResponse.json();
                console.log("userRecord", userRecord);
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
  <div class="border border-gray-300 rounded-xl shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out">
      <h1 class="text-3xl font-bold p-2">{title}</h1>
      {#if subtitle}
        <p class="text-gray-500 px-2">{subtitle}</p>
      {/if}
      {#if events?.length == 0}
          <div class="flex flex-col md:flex-row overflow-x-auto mt-3">
            <div class="flex flex-col items-center justify-center w-full h-full py-10">
              <p class="text-gray-600 text-lg font-semibold">No events available at the moment.</p>
              <p class="text-gray-500 text-sm mt-2">Please check back later.</p>
            </div>
          </div>


      {:else}

      <div class="flex flex-col md:flex-row overflow-x-auto {subtitle? "mt-3":"mt-6"}">

        {#each events as event}
          <EventCard {event} {toggleRSVP} {RSVP} {RSVPEnabled} on:sendToHome={handleEventClick}/>
        {/each}
      </div>

      {/if}
  </div>

</div>