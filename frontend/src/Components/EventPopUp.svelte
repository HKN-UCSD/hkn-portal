<script>
    import { createEventDispatcher, onMount } from "svelte";
    import CustomizableEventConsole from "./Events/CustomizableEventConsole.svelte";
    import EventPopUpButtons from "./Events/EventPopUpButtons.svelte"
    import "./Events/eventutils";
    import {
        addToCalendar,
    } from "./Events/eventutils";
    import { marked } from 'marked';
    import DOMPurify from 'dompurify';

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    export let event;
    let selectedEvent = event.detail
    let selectedEventLocation = selectedEvent.location?.trim() || "No Location Specified";
    const dispatch = createEventDispatcher();

    $: parsedDescription = DOMPurify.sanitize(marked.parse(selectedEvent?.description || ""));

    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then((value) =>
            value.json(),
        );
        return response.is_admin;
    }

    function toggleAttendeeView() {
        showAttendee = !showAttendee;
    }

    function close() {
        dispatch("close"); // Emits the close event to the parent (Home.svelte)
    }
    
    
    $: start_time = new Date(selectedEvent.start_time);
    $: end_time = new Date(selectedEvent.end_time);
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
    

    const formattedDateTime = getFormattedDateTime(event.detail.start_time, event.detail.end_time);
    const [eventDate, eventTime] = formattedDateTime.split(", ");
        
    let isAdmin = false; 
    let showAttendee = false;

    async function getAllFeatures(){
        isAdmin = await checkAdmin();
    }

    const bgClassMap = {
        Technical: 'bg-technical',
        Social: 'bg-social',
        Professional: 'bg-professional',
        Outreach: 'bg-outreach',
        Mentorship: 'bg-mentorship',
        General: 'bg-general'
    };

    onMount(() => {
        getAllFeatures();
        if (!event) {
            close() // Close if no event is provided
        }
    });
</script>

{#if event}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 px-4" on:click={close}>
    <!-- Wrap modal + button in a flex column to center everything vertically -->
    <div class="flex flex-col items-center gap-4 w-full max-w-2xl" on:click|stopPropagation>
      
      <!-- MODAL - Make this clickable -->
      <div 
        class="relative bg-white p-4 sm:p-6 rounded-lg shadow-lg w-full max-h-[90vh] overflow-y-auto scrollbar-hide">
        
        {#if showAttendee == false}
          <!-- Event Image -->
          <img
            src={selectedEvent.embed_code}
            alt={selectedEvent.title}
            class="w-full max-h-60 sm:max-h-96 object-cover rounded-lg"
          />

          <!-- Event Type and Points -->
          <div class="flex flex-wrap justify-start mt-5 gap-2">
            <div class={`${bgClassMap[selectedEvent.event_type]} text-${selectedEvent.event_type === "Professional" ? "black" : "white"} font-semibold text-sm px-3 py-1 rounded-full`}>
              {selectedEvent.event_type}
            </div>
            <div class="bg-secondary bg-opacity-50 text-primary font-semibold text-sm px-3 py-1 rounded-full">
              +{selectedEvent.points} points
            </div>
          </div>

          <!-- Title and Time -->
          <div class="flex flex-col sm:flex-row justify-between mt-4 gap-2">
            <div class="text-2xl sm:text-3xl text-blue-800 font-semibold break-words sm:w-3/5">
              <h2>{selectedEvent.title}</h2>
            </div>
            <div class="text-lg sm:text-2xl text-black-800 font-semibold text-right sm:w-2/5">
              <p>{eventDate}</p>
              <p>{eventTime}</p>
            </div>
          </div>

          <!-- Location and Add to Calendar -->
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mt-2 gap-2">
            <div class="text-base sm:text-lg text-black-800 font-semibold">
              📍 {selectedEventLocation}
            </div>
            <button 
              class="text-base sm:text-lg border-2 px-2 py-1 border-secondary rounded-lg transition-transform transform hover:scale-105 hover:bg-secondary hover:text-white"
              on:click|stopPropagation={() => addToCalendar(selectedEvent)}
            >
              +📅
            </button>
          </div>

          <!-- Description -->
          <div class="text-gray-700 text-sm font-semibold leading-relaxed mt-4 break-words">
            <div class="description prose" >
              {@html parsedDescription}
            </div>
            <EventPopUpButtons event={selectedEvent} />
          </div>

          <!-- Visual indicator for admins -->
          {#if isAdmin}
            <div class="w-full flex justify-center mt-4">
              <button
                class="mt-3 py-2 px-4 bg-gray-200 text-gray-800 rounded font-semibold hover:bg-gray-300"
                on:click|stopPropagation={toggleAttendeeView}
              >
                View Attendees →
              </button>
            </div>
          {/if}
        {/if}

        {#if showAttendee == true}
          <CustomizableEventConsole event={selectedEvent} time={eventTime} date={eventDate} />
          
          <!-- Back hint for admins -->
          {#if isAdmin}
            <div class="w-full flex justify-center mt-4">
              <button
                class="mt-3 py-2 px-4 bg-gray-200 text-gray-800 rounded font-semibold hover:bg-gray-300"
                on:click|stopPropagation={toggleAttendeeView}
              >
                ← Back to Event
              </button>
            </div>
          {/if}
        {/if}
      </div>

      <!-- Remove the button section completely -->
    </div>
  </div>
{/if}

<style>
  .clickable {
    cursor: pointer;
    transition: transform 0.2s ease;
  }

  .clickable:hover {
    transform: scale(1.01);
  }

  .click-hint {
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 0.7;
    }
    50% {
      opacity: 1;
    }
  }

</style>