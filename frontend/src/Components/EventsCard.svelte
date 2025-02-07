
<script>
    import { onMount } from "svelte";
    import {navigate} from "svelte-routing";
    import {requestAction, deleteAction} from "./Events/eventutils";


    // Get passed in data
    export let title;
    export let subtitle;
    export let events;

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

  <div class="container mx-auto text-primary">
    <div class="border border-gray-300 rounded-lg shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out">
        <h1 class="text-3xl font-bold  mb-8">{title}</h1>
        {#if subtitle}
          <p class="text-gray-500">{subtitle}</p>
        {/if}
        <div class="flex flex-col md:flex-row max-h-[800px] overflow-x-auto">
          {#each events as event}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="flex-none md:basis-1/2 lg:basis-1/3 bg-white border border-gray-300 rounded-lg min-h-10 m-2 rounded-lg shadow-md overflow-hidden hover:bg-gray-100 transition duration-300 flex flex-col" on:click={() => navigate(event.url)}>
              <div class="canva-embed-code">
                {@html event.embed_code}
              </div>
              <!-- Content Section -->
              <div class="p-6 flex-1 flex flex-col justify-between bg-white ">
                <div>
                  <h2 class="text-xl font-semibold text-gray-900 mb-2">{event.title}</h2>
                  <p class="text-gray-600 flex items-center gap-2 mb-2">
                    📍 {event.location}
                  </p>
                  <p class="text-gray-600 flex items-center gap-2">
                    🕒 {new Date(event.start_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })},
                    {new Date(event.start_time).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: true })}
                  </p>
                </div>
              </div>

              <!-- Button Section -->
              <div class="p-4">
                <button
                  class="w-full text-white py-2 px-4 rounded transition duration-300 {
                    RSVP.find((record) => record.event == event.pk)
                      ? 'bg-primary hover:bg-secondary'
                      : 'bg-secondary hover:bg-primary'
                  }"
                  on:click={(e) => toggleRSVP(event, e)}
                >
                  RSVP
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
  </div>
