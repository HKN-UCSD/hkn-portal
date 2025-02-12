
<script>
    import { navigate } from "svelte-routing";
    import { requestAction, deleteAction } from "./Events/eventutils";
    import { onDestroy } from "svelte";
    import { userStore } from "../stores";
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    function handleClick(event) {
        dispatch("eventClick", event);
    }

    // Get passed in data
    export let title;
    export let subtitle;
    export let events;

    // Get user data
    let userData = null
    let user = null;
    const unsubscribe = userStore.subscribe((value) => user = value);
    onDestroy(unsubscribe);

    
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
  </script>

  <div class="container mx-auto text-primary">
    <div class="border border-gray-300 rounded-lg shadow-md p-6 hover:shadow-xl transform transition-transform duration-300 ease-in-out active:bg-gray-100">
        <h1 class="text-3xl font-bold  mb-8">{title}</h1>
        {#if subtitle}
          <p class="text-gray-500">{subtitle}</p>
        {/if}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-[900px] overflow-y-auto">
          {#each events as event}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="bg-white rounded-lg shadow-lg overflow-hidden hover:scale-105 transition duration-300" >
              <div class="p-6" on:click={()=>handleClick(event)}>
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
