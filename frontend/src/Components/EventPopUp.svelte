<script>
    import { createEventDispatcher, onMount } from "svelte";
    import CustomizableEventConsole from "./Events/CustomizableEventConsole.svelte";
    import EventPopUpButtons from "./Events/EventPopUpButtons.svelte"
    import "./Events/eventutils";
    import {
        addToCalendar,
    } from "./Events/eventutils";

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    export let event;
    let selectedEvent = event.detail
    let selectedEventLocation = selectedEvent.location?.trim() || "No Location Specified";
    const dispatch = createEventDispatcher();

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
    <!-- Change EventPopUp View from attendee to event details-->
    {#if isAdmin == true}
        <button
            class="fixed top-5 right-5 bg-gray-700 text-white px-4 py-2 rounded-lg shadow-md hover:bg-gray-700 transition-all z-[100]"
            on:click={toggleAttendeeView}
        >
        {showAttendee ? "Back to Event" : "Switch View"}
        </button>
    {/if}

    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" on:click={close}>
        <!-- Installed new package called scrollbar-hide -->
        <div class="relative bg-white p-6 rounded-lg shadow-lg max-w-lg sm:max-w-xl md:max-w-2xl w-full max-h-[100vh] overflow-y-auto scrollbar-hide " on:click|stopPropagation>
            {#if showAttendee == false}
                <!-- Event Image -->
                <img src={selectedEvent.embed_code} alt={selectedEvent.title} class="w-full h-full object-cover rounded-lg" />
                    <!-- Event Type and Points -->
                    <div class="flex justify-start mt-5">
                        <div class={`${bgClassMap[selectedEvent.event_type]} text-${selectedEvent.event_type === "Professional" ? "black" : "white"} font-semibold text-sm px-3 py-1 rounded-full mr-2`}>
                            {selectedEvent.event_type}
                        </div>
                        <div class="bg-secondary bg-opacity-50 text-primary font-semibold text-sm px-3 py-1 rounded-full">
                            +{selectedEvent.points} points
                        </div>
                    </div>
                    <!-- Event Title and Time -->
                    <div class="flex justify-between w-full">
                        <div class="text-3xl text-blue-800 font-semibold mt-2 w-80">
                            <h2>{selectedEvent.title}</h2>
                        </div>
                        <div class="text-2xl text-black-800 font-semibold mt-2 w-60 text-right">
                            <p>{eventDate}</p>
                            <p>{eventTime}</p>
                        </div>
                    </div>
                    <!-- Event Location and Add to Calendar -->
                    <div class="flex justify-between w-full mt-1 p-1 mb-1">
                        <div class="text-lg text-black-800 font-semibold">
                            <p>
                                📍 {selectedEventLocation}
                            </p>
                        </div>
                        <button 
                            class="text-lg border-2 px-1 border-secondary rounded-lg transition-transform transform hover:scale-105 hover:bg-secondary hover:text-white"
                            on:click={() => addToCalendar(selectedEvent)}
                        >
                            +📅
                        </button>
                </div>
                    <div class="text-gray-700 text-sm font-semibold leading-relaxed max-h-32 break-words">
                        {selectedEvent.description}
                        <EventPopUpButtons event={selectedEvent}/>
                    </div>
                {/if}
                {#if showAttendee == true}
                    <CustomizableEventConsole event={selectedEvent} /> 
                {/if}

            </div>

    </div>
{/if}
