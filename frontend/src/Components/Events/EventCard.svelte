
<script>
  import { navigate } from 'svelte-routing';
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
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="flex-none md:basis-1/2 lg:basis-1/3 border border-gray-300 rounded-lg min-h-10 m-2 bg-white rounded-lg shadow-md overflow-hidden hover:bg-gray-100 transition duration-300 flex flex-col" on:click={dispatchEvent(event)}>
  <div class="canva-embed-code max-h-[200px] overflow-hidden">
    {@html event.embed_code}
  </div>
  <!-- Content Section -->
  <div class="flex-grow p-6 flex flex-col overflow-x-auto">
      <h2 class="text-xl font-semibold text-gray-900 mb-2">{event.title}</h2>
      <p class="text-gray-600 flex items-center gap-2 mb-2">
        📍 {event.location}
      </p>
      <p class="text-gray-600 flex items-center gap-2">
        🕒 {getFormattedDateTime(event.start_time, event.end_time)}
      </p>
  </div>

  <!-- Button Section -->

  {#if RSVPEnabled}

  <div class="p-6">
    <button
        class="w-full py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105 focus:outline-none  shadow-lg
            {RSVP.find((record) => record.event == event.pk)
                ? 'bg-primary hover:bg-primary-dark focus:ring-primary'
                : 'bg-secondary hover:bg-secondary-dark focus:ring-secondary'
            }"
        on:click={(e) => toggleRSVP(event, e)}
    >
        {RSVP.find((record) => record.event == event.pk) ? "RSVP'd ★" : "RSVP"}
    </button>
</div>
  {/if}
</div>