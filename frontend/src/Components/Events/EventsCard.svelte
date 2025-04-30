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
    let eventsContainer; // Reference to the scrollable container


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
      deleteAction(RSVP.find((record) => record.event == event.pk).pk);
    } else {
      await requestAction(event, "RSVP",userData);
      }
    await getUserData();
  }

  // Function to scroll left
  function scrollLeft() {
    if (eventsContainer) {
      eventsContainer.scrollBy({ left: -300, behavior: 'smooth' });
    }
  }

  // Function to scroll right
  function scrollRight() {
    if (eventsContainer) {
      eventsContainer.scrollBy({ left: 300, behavior: 'smooth' });
    }
  }

  onMount(async () => {
    // Fetch events from the server
    await new Promise((resolve) => {
        getUserData();
        resolve();
      });
      const curr = new Date().toISOString();
  });


</script>

<div class="mx-5 bg-gray-50 md:mx-auto text-primary">
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
      <!-- Events container with horizontal scrolling -->
      <div class="relative">
        <div 
          bind:this={eventsContainer}
          class="flex flex-col md:flex-row overflow-x-auto {subtitle? "mt-3":"mt-6"} pb-10"
          on:wheel={(event) => {
            // Convert vertical scroll to horizontal scroll
            event.preventDefault();
            const scrollAmount = event.deltaY || event.deltaX;
            eventsContainer.scrollLeft += scrollAmount;
          }}
        >
          {#each events as event}
            <EventCard 
              event={event} 
              toggleRSVP={toggleRSVP} 
              RSVP={RSVP} 
              RSVPEnabled={RSVPEnabled} 
              on:sendToHome={handleEventClick}
            />
          {/each}
        </div>
        
        <!-- Navigation buttons -->
        <div class="flex justify-between absolute w-full top-1/2 transform -translate-y-1/2 px-2 pointer-events-none">
          <button 
            class="bg-white text-primary rounded-full p-2 shadow-md hover:bg-gray-100 focus:outline-none pointer-events-auto z-10 opacity-80 hover:opacity-100 transition-opacity"
            on:click={scrollLeft}
            aria-label="Scroll left">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <button 
            class="bg-white text-primary rounded-full p-2 shadow-md hover:bg-gray-100 focus:outline-none pointer-events-auto z-10 opacity-80 hover:opacity-100 transition-opacity"
            on:click={scrollRight}
            aria-label="Scroll right">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- Bottom navigation arrows with scrollbar -->
        <div class="flex items-center justify-center mt-2">
          <button 
            class="text-primary p-1 mx-1 hover:bg-gray-200 rounded-full focus:outline-none"
            on:click={scrollLeft}
            aria-label="Scroll left">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <div class="relative w-32 h-2 bg-gray-200 rounded-full mx-2">
            <!-- This is a simplified scrollbar visualization -->
            <div class="absolute top-0 left-0 h-full bg-primary rounded-full" style="width: {Math.min(100, events.length > 0 ? 100 / (events.length / 3) : 100)}%; min-width: 10%;"></div>
          </div>
          
          <button 
            class="text-primary p-1 mx-1 hover:bg-gray-200 rounded-full focus:outline-none"
            on:click={scrollRight}
            aria-label="Scroll right">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
      {/if}
  </div>
</div>