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
    let cardWidth = 0; // Width of two cards plus gap


    async function getUserData() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/profile/self/`);
            if (response.ok) {
                userData = await response.json();
                let userRecordResponse = await fetch(`http://127.0.0.1:8000/api/eventactionrecords/user/${userData.user_id}/`);
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

  // Function to scroll left by exactly 2 cards
  function scrollLeft() {
    if (eventsContainer) {
      calculateCardWidth();
      eventsContainer.scrollBy({ left: -cardWidth, behavior: 'smooth' });
    }
  }

  // Function to scroll right by exactly 2 cards
  function scrollRight() {
    if (eventsContainer) {
      calculateCardWidth();
      eventsContainer.scrollBy({ left: cardWidth, behavior: 'smooth' });
    }
  }

  // Calculate the width of two cards + gap
  function calculateCardWidth() {
    if (eventsContainer && eventsContainer.children.length >= 3) {
      // Get the first three cards
      const firstCard = eventsContainer.children[0];
      const thirdCard = eventsContainer.children[2];
      
      // Use getBoundingClientRect to get precise positions
      const firstCardRect = firstCard.getBoundingClientRect();
      const thirdCardRect = thirdCard.getBoundingClientRect();
      
      // Calculate distance from left edge of first card to left edge of third card
      // This is exactly 2 cards width + 2 gaps, ensuring perfect alignment
      cardWidth = thirdCardRect.left - firstCardRect.left;
    } else if (eventsContainer && eventsContainer.children.length > 0) {
      // If we have less than 3 cards, use single card width x 2
      const singleCard = eventsContainer.children[0].getBoundingClientRect();
      // Estimate the width of two cards (including gap)
      cardWidth = singleCard.width * 2.25; // Add 25% to account for the gap
    }
  }

  onMount(async () => {
    // Fetch events from the server
    await new Promise((resolve) => {
        getUserData();
        resolve();
      });
      const curr = new Date().toISOString();
      
      // Calculate initial card width after the DOM is fully rendered
      setTimeout(calculateCardWidth, 100);
      
      // Recalculate on window resize
      window.addEventListener('resize', calculateCardWidth);
  });


</script>

<div class="mx-5 bg-gray-50 md:mx-auto text-primary">
  <div class="border border-gray-300 rounded-xl shadow-md px-4 py-5 hover:shadow-xl transform transition-transform duration-300 ease-in-out">
      <h1 class="text-2xl font-bold py-1 pl-5 pr-1">{title}</h1>
      {#if subtitle}
        <p class="text-gray-500 py-0 pl-5 pr-1">{subtitle}</p>
      {/if}
      {#if events?.length == 0}
          <div class="flex flex-col md:flex-row overflow-x-auto mt-2">
            <div class="flex flex-col items-center justify-center w-full h-full py-8">
              <p class="text-gray-600 text-lg font-semibold">No events available at the moment.</p>
              <p class="text-gray-500 text-sm mt-2">Please check back later.</p>
            </div>
          </div>


      {:else}
      <!-- Events section with container and navigation buttons -->
      <div class="flex items-stretch mt-2">
        <!-- Left button - hidden on mobile (below md breakpoint) -->
        <div class="hidden md:flex flex-none items-center pr-1">
          <button 
            class="bg-white text-primary rounded-full p-1.5 shadow-md hover:bg-gray-100 focus:outline-none z-10 transition-colors hover:shadow-lg"
            on:click={scrollLeft}
            aria-label="Scroll left">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>
        
        <!-- Events container with horizontal scrolling -->
        <div class="flex-grow overflow-hidden">
          <div 
            bind:this={eventsContainer}
            class="flex flex-col md:flex-row overflow-x-auto gap-3"
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
        </div>
        
        <!-- Right button - hidden on mobile (below md breakpoint) -->
        <div class="hidden md:flex flex-none items-center pl-1">
          <button 
            class="bg-white text-primary rounded-full p-1.5 shadow-md hover:bg-gray-100 focus:outline-none z-10 transition-colors hover:shadow-lg"
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