
<script>
    import { onMount } from "svelte";
    import {getEvents} from "./Events/eventstore";
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
        const a = await requestAction(event, "RSVP",userData);
        }
      await getUserData();
    }


    onMount(async () => {
      // Fetch events from the server
        await getUserData();
        const res = await getEvents()
        const curr = new Date().toISOString();
        console.log("res", res);
      // filter by start time and only show title and description
        events = res.filter(event => event.start_time > curr).map(event => ({title: event.name, description: event.description, pk: event.pk, url: `/events/${event.pk}`}));
        console.log("event", events);
    });


  </script>

  <div class="container mx-auto text-primary">
    <div class="border border-gray-300 rounded-lg shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out active:bg-gray-100">
        <h1 class="text-3xl font-bold  mb-2">{title}</h1>
        {#if subtitle}
          <p class="text-gray-500">{subtitle}</p>
        {/if}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-[900px] overflow-y-auto">
          {#each events as event}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="bg-white rounded-lg shadow-lg overflow-hidden hover:scale-105 transition duration-300" on:click={()=> navigate(event.url)}>
              <div class="p-6">
                <h2 class="text-xl font-semibold mb-4 ">{event.title}</h2>
                <div class="text-gray-700 overflow-hidden min-h-[120px] max-h-[120px] relative">
                    <p class="m-0">{event.description}</p>
                    <!-- Fade-out effect -->
                    <div class="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-white to-transparent"></div>
                  </div>
              </div>
              <div class="p-4 bg-gray-50">
                <button class="w-full text-white py-2 px-4 rounded  transition duration-300 {
            RSVP.find((record) => record.event == event.pk)
            ? 'bg-primary hover:bg-secondary'
            : 'bg-secondary hover:bg-primary'
        }" on:click={(e) => toggleRSVP(event, e)}>
                  RSVP
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
  </div>
