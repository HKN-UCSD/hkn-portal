
<script>
    import { navigate } from 'svelte-routing';
    export let event;
    export let toggleRSVP;
    export let RSVP;
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
<div class="flex-none md:basis-1/2 lg:basis-1/3 border border-gray-300 rounded-lg min-h-10 m-2 bg-white rounded-lg shadow-md overflow-hidden hover:bg-gray-100 transition duration-300 flex flex-col" 
on:click={dispatchEvent(event)}>
    <div class="canva-embed-code">
      {@html event.embed_code}
    </div>
    <!-- Content Section -->
    <div class="p-6 flex-1 flex flex-col justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">{event.title}</h2>
        <p class="text-gray-600 flex items-center gap-2 mb-2">
          📍 {event.location}
        </p>
        <p class="text-gray-600 flex items-center gap-2">
          🕒 {getFormattedDateTime(event.start_time, event.end_time)}
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