<script>
    // NO PORTRAIT PHOTOS
    export let event;
    let selectedEvent = event.detail
    import { createEventDispatcher, onMount } from "svelte";
    import CustomizableEventConsole from "./Events/CustomizableEventConsole.svelte";
    import EventPopUpButtons from "./Events/EventPopUpButtons.svelte"
    import "./Events/eventutils";
    import {
        addToCalendar,
    } from "./Events/eventutils";
    let showOverlay = false;

    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then((value) =>
            value.json(),
        );
        return response.is_admin;
    }

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    function toggleAttendeeView() {
        showAttendee = !showAttendee;
    }

    const dispatch = createEventDispatcher();
    // If no event is provided, close the modal
    function close() {
        dispatch("close"); // Emits the close event to the parent (Home.svelte)
    }
    if (!event) {
        close() // Close if no event is provided
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

    // Variables Used For Dynamic Resizing, Unused for Now as there are no Square Banners
    /*
    let imageSrc = event.detail.embed_code; 
    let layoutClass = "landscape"; // Default
    let aspectRatio = 1; // Default aspect ratio
    */
    // Extracts Ratio of Image, Used for Dynamic Layout Resizing
    /*
    function extractAspectRatio(embedCode) {
        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = embedCode; // Parse the HTML string

        // Find the <div> with a `padding-top` style (Canva uses this to maintain aspect ratio)
        const container = tempDiv.querySelector("div[style*='padding-top']");
        if (container) {
            const paddingMatch = container.style.paddingTop.match(/([\d.]+)%/);
            if (paddingMatch) {
                const paddingPercentage = parseFloat(paddingMatch[1]); // Convert to number
                const ratio = paddingPercentage / 100; // Convert to aspect ratio

                console.log("Extracted Aspect Ratio:", ratio);
                return ratio;
            }
        }
        console.warn("No padding-top found in Canva embed.");
        return 1; // Default to 1:1 aspect ratio
    }
    */

    // Below is code for Dynamic Layout Resizing, For now we will not need it as there are no Square Banners
    /*
    $: layoutClass = aspectRatio >= 0.9 && aspectRatio <= 1.1 ? "square" : "landscape";
    onMount(() => {
        aspectRatio = extractAspectRatio(imageSrc);
    });
    */
    onMount(() => {
        getAllFeatures();
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
                    <div class="flex justify-between w-full">
                        <div class="text-3xl text-blue-800 font-semibold mt-4 w-80">
                            <h2>{selectedEvent.title}</h2>
                        </div>
                        <div class="text-2xl text-black-800 font-semibold mt-4 w-60 text-right">
                            <p>{eventDate}</p>
                            <p>{eventTime}</p>
                        </div>
                    </div>
                    
                    <div class="flex justify-between w-full mt-2">
                        <div class="text-lg text-black-800 font-semibold">
                            <p>
                                📍 {selectedEvent.location}
                            </p>
                        </div>
                        <button 
                            class="text-lg border-2 px-1 border-secondary rounded-lg transition-transform transform hover:scale-105 hover:bg-secondary hover:text-white"
                            on:click={() => addToCalendar(selectedEvent)}
                        >
                            +📅
                        </button>
                </div>
                    <!-- Event Description -->
                    <div class="text-gray-700 text-sm font-semibold leading-relaxed max-h-32 break-words">
                        {selectedEvent.description}
                        <EventPopUpButtons event={selectedEvent}/>
                    </div>
                    
                {/if}
                {#if showAttendee == true}
                    <CustomizableEventConsole event={selectedEvent} /> 
                {/if}

            </div>

        
        <!-- Future Dynamic Resizing, As Square Banners Have Been Deleted -->
        <!--
        {#if layoutClass == "square"}
            <div class="relative bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[800vh] overflow-y-auto scrollbar-hide gap-4" on:click|stopPropagation>
                {#if showAttendee == false}
                    <div class="flex space-x-6">
                        <div class="w-2/5 canva-embed-code w-130 h-130 object-cover rounded-lg hidden sm:block">
                            {@html event.detail.embed_code}
                        </div>
                        <div class="w-full sm:w-3/5">
                            <div class="flex justify-between w-full">
                                <div class="text-3xl text-primary-500 font-semibold mt-4 w-64">
                                    <h2>{event.detail.title}</h2>
                                </div>
                                <div class="text-2xl text-black-800 font-semibold mt-4 w-60 text-right">
                                    <p>{eventDate}</p>
                                    <p>{eventTime}</p>
                                </div>
                            </div>
                            <div class="text-lg text-black-800 mt-2 font-semibold">
                                <p>
                                    📍 {event.detail.location}
                                </p>
                            </div>
                            <div class="w-full max-w-md h-48 bg-gray-50 overflow-y-auto rounded-md whitespace-normal break-words scrollbar-hide">
                                <p class=" black-600 font-normal leading-relaxed">{event.detail.description}</p>
                            </div>

                            <EventPopUpButtons event={selectedEvent.detail}/>
                        </div>
                        
                    </div>
                    
                {/if}
                {#if showAttendee == true}
                    <CustomizableEventConsole event={selectedEvent.detail} />
                {/if}
                
            </div>
        {/if}
        -->
    </div>
{/if}
