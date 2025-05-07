
<script>
  import { navigate } from 'svelte-routing';
  import { eventGraphics } from './EventGraphics.js';
  export let event;
  export let toggleRSVP;
  export let RSVP;
  export let RSVPEnabled = true;
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  function dispatchEvent(event) {
      dispatch('sendToHome', event);
  }
    
  function getFormattedDateTime(startDateTimeString, endDateTimeString) {
      const startEventTime = new Date(startDateTimeString);
      const endEventTime = new Date(endDateTimeString);
      const options = {
          month: 'short', // Month abbreviation (e.g., Oct)
          day: 'numeric', // Day of the month (e.g., 22)
          hour: 'numeric', // Hour in 12-hour format (e.g., 6)
          minute: '2-digit', // Minutes (e.g., 00)
          hour12: true // Use 12-hour clock (e.g., AM/PM)
          };
          if (startEventTime.toLocaleString('en-US', options).split(',')[0] == endEventTime.toLocaleString('en-US', options).split(',')[0]){
              return startEventTime.toLocaleString('en-US', options).concat(" -", endEventTime.toLocaleString('en-US', options).split(',')[1])
          }else{
              return startEventTime.toLocaleString('en-US', options).concat(" - ", endEventTime.toLocaleString('en-US', options))
          }
      }
   /* if current time > event end time, disable */
   if (new Date() > new Date(event.end_time) || event.is_draft) {
       RSVPEnabled = false;
   }

</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div id="event-{event.pk}"
  class="flex-shrink-0 w-[90vw] sm:w-[40vw] lg:w-[21vw] h-[50vh] min-h-[300px] max-w-[500px] border border-gray-300 rounded-lg m-2 bg-white shadow-md overflow-hidden transition duration-300 flex flex-col"
  class:bg-gray-300={event.is_draft}
  class:border-gray-600={event.is_draft}
  class:border-4={event.is_draft}
  class:hover:bg-gray-100={!event.is_draft}
  on:click={() => dispatchEvent(event)}
>
  <!-- Embed Section -->
  <div class="canva-embed-code overflow-hidden">
    {#if Object.values(eventGraphics).includes(event.embed_code)}
      <img src={event.embed_code} alt={event.title} class="w-full h-full object-cover" />
    {:else}
      <div class="absolute inset-0 w-full h-full [&>iframe]:w-full [&>iframe]:h-full [&>iframe]:absolute [&>iframe]:top-0 [&>iframe]:left-0">
        {@html event.embed_code}
      </div>
    {/if}
  </div>

  <!-- Content & RSVP Section -->
  <div class="flex-grow px-6 py-4 flex flex-col justify-between overflow-hidden">
    <!-- Title -->
    <h2 class="text-xl font-semibold text-gray-900 mb-1">
      {event.title}
      {#if event.is_draft}
        <span class="text-sm text-gray-500">(Unpublished)</span>
      {/if}
    </h2>

    <!-- Location -->
    <p class="text-gray-600 flex items-center gap-2 text-sm mb-1">
      📍 {event.location?.trim() || "No Location Specified"}
    </p>

    <!-- Time -->
    <p class="text-gray-600 flex items-center gap-2 text-sm mb-4">
      🕒 {getFormattedDateTime(event.start_time, event.end_time)}
    </p>

    <!-- RSVP Button -->
    {#if RSVPEnabled}
      <button
        class="mt-auto w-full py-1 px-4 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105 focus:outline-none shadow-lg
          {RSVP.find((record) => record.event == event.pk)
              ? 'bg-primary'
              : 'bg-secondary'
          }"
        on:click={(e) => toggleRSVP(event, e)}
      >
        {RSVP.find((record) => record.event == event.pk) ? "RSVP'd ★" : "RSVP"}
      </button>
    {/if}
  </div>
</div>
