<script>
    // NO PORTRAIT PHOTOS
    import { onMount } from "svelte";
    export let event;
    let selectedEvent = event
    import { createEventDispatcher } from "svelte";
    import CustomizableEventConsole from "./Events/CustomizableEventConsole.svelte";

    let imageSrc = event.detail.embed_code; 
    let layoutClass = "landscape"; // Default
    let aspectRatio = 1; // Default aspect ratio
    let showAttendee = false;

    export async function getPermissions() {
        let response = await fetch(`/api/permissions/`);
        return await response.json();
    }

    // Extracts Ratio of Image
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

    function toggleAttendeeView() {
        showAttendee = !showAttendee;
        console.log("attendee view changed")
    }

    const dispatch = createEventDispatcher();
    // If no event is provided, close the modal
    function close() {
        dispatch("close"); // Emits the close event to the parent (Home.svelte)
    }
    if (!event) {
        close() // Close if no event is provided
    }
    
    $: start_time = new Date(event.detail.start_time);
    $: end_time = new Date(event.detail.end_time);
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

    $: layoutClass = aspectRatio >= 0.9 && aspectRatio <= 1.1 ? "square" : "landscape";
    onMount(() => {
        aspectRatio = extractAspectRatio(imageSrc);
    });
</script>

{#if event}
    <!-- Change EventPopUp View from attendee to event details-->
    <button
        class="fixed top-5 right-5 bg-gray-700 text-white px-4 py-2 rounded-lg shadow-md hover:bg-gray-700 transition-all z-[100]"
        on:click={toggleAttendeeView}
    >
    {showAttendee ? "Back to Event" : "Switch View"}
    </button>

    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50" on:click={close}>
        {#if layoutClass == "landscape"}
            <!-- Installed new package called scrollbar-hide -->
            <div class="relative bg-white p-6 rounded-lg shadow-lg max-w-lg sm:max-w-xl md:max-w-2xl w-full max-h-[100vh] overflow-y-auto scrollbar-hide" on:click|stopPropagation>
                {#if showAttendee == false}
                    <!-- Event Image -->
                    <div class="mx-auto w-full canva-embed-code h-auto overflow-hidden rounded-md" >
                        {@html event.detail.embed_code}
                    </div>
                    <div class="flex justify-between w-full">
                        <div class="text-3xl text-blue-800 font-semibold mt-4 w-80">
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

                    <!-- Event Description -->
                    <div class="text-gray-700 mt-3 text-sm leading-relaxed max-h-32 break-words">
                        {event.detail.description}
                    </div>

                {/if}
                {#if showAttendee == true}
                    <div on:click|stopPropagation>
                        <CustomizableEventConsole event={selectedEvent.detail} />
                    </div>
                {/if}

            </div>
        {/if}
            
        {#if layoutClass == "square"}
            <div class="relative bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[800vh] overflow-y-auto scrollbar-hide" on:click|stopPropagation>
                {#if showAttendee == false}
                    <!-- left side -->
                    <div class="flex space-x-6">
                        <div class="w-2/5 canva-embed-code w-130 h-130 object-cover rounded-lg hidden sm:block">
                            {@html event.detail.embed_code}
                        </div>
                        <div class="w-full sm:w-3/5">
                            <div class="flex justify-between w-full">
                                <div class="text-3xl text-blue-800 font-semibold mt-4 w-64">
                                    <h2>{event.detail.title}</h2>
                                </div>
                                <div class="text-2xl text-black-800 font-semibold mt-4 w-60 text-right">
                                    <p>{eventDate}</p>
                                    <p>{eventTime}</p>
                                </div>
                            </div>
                            <!-- Event Time & Date + Location-->
                            <div class="text-lg text-black-800 mt-2 font-semibold">
                                <p>
                                    📍 {event.detail.location}
                                </p>
                            </div>
                            <!-- Event Description, prevents overflow on the x axis. Breaks Words-->
                            <div class="w-full max-w-md h-48 bg-gray-50 overflow-y-auto rounded-md whitespace-normal break-words scrollbar-hide">
                                <p class=" black-600 font-normal leading-relaxed">{event.detail.description}</p>
                            </div>
                        </div>
                    </div>
                {/if}
                {#if showAttendee == true}
                    <CustomizableEventConsole event={selectedEvent.detail} />
                {/if}
            </div>
        {/if}
    </div>
{/if}
