
<script>
    import { onMount } from "svelte";
    import {getEvents} from "./Events/eventstore";
    import {navigate} from "svelte-routing";
    import {requestAction, deleteAction} from "./Events/eventutils";
    import { onDestroy } from "svelte";
    import {userStore} from "../stores";


    // Define your event data
    let events = [];
    let userData = null
    let user = null;
    const unsubscribe = userStore.subscribe((value) => user = value);
    onDestroy(unsubscribe);


    async function getUserData() {
        try {
            const response = await fetch(`/api/profile/self/`);

            if (response.ok) {
                userData = await response.json();
            } else {
                console.error("Failed to fetch self data");
            }

        } catch (error) {
            console.error("Error fetching user data", error);
        }
    }
    let rsvpEvents = new Set();
    async function toggleRSVP(event, e) {

      e.stopPropagation(); // Stop the event from bubbling up to the parent

      rsvpEvents = new Set(rsvpEvents); // Create new Set for reactivity
      console.log("event", event);
      let eventId = event.id;
      if (rsvpEvents.has(eventId)) {
        rsvpEvents.delete(eventId);
        console.log("user", user.records);
        deleteAction(userData.records);
      } else {
        rsvpEvents.add(eventId);
        requestAction(event, "RSVP",userData);

        }

      rsvpEvents = new Set(rsvpEvents); // Update the Set
      console.log("rsvp", rsvpEvents);


    }


    onMount(async () => {
      // Fetch events from the server
        await getUserData();
        const res = await getEvents()
        const curr = new Date().toISOString();
        console.log("res", res);
      // filter by start time and only show title and description
        events = res.filter(event => event.start_time > curr).map(event => ({title: event.name, description: event.description, id: event.pk, url: `/events/${event.pk}`}));
        console.log("event", events);
    });


  </script>

  <div class="container mx-auto text-primary">
    <div class="border border-gray-300 rounded-lg shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out active:bg-gray-100">
        <h1 class="text-3xl font-bold  mb-8">Upcoming Events</h1>
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
          rsvpEvents.has(event.id)
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
