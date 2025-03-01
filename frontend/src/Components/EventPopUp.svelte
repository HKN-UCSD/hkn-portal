<script>
    // NO PORTRAIT PHOTOS
    import { onMount } from "svelte";
    export let event;
    import { createEventDispatcher } from "svelte";

    let imageSrc = event.detail.embed_code; 
    let layoutClass = "landscape"; // Default
    let aspectRatio = 1; // Default aspect ratio
    let showAttendee = false;

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

    $: layoutClass = aspectRatio >= 0.9 && aspectRatio <= 1.1 ? "square" : "landscape";
    onMount(() => {
        aspectRatio = extractAspectRatio(imageSrc);
        console.log("Final Layout Class:", layoutClass);
    });
</script>

{#if event}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        {#if layoutClass == "landscape"}
            <div class="relative bg-white p-6 rounded-lg shadow-lg max-w-xl w-full max-h-[100vh]">
                <button
                    class="fixed top-5 right-5 bg-gray-700 text-white px-4 py-2 rounded-lg shadow-md hover:bg-gray-700 transition-all"
                    on:click={toggleAttendeeView}
                >
                    {showAttendee ? "Back to Event" : "Switch View"}
                </button>

                <!-- Close Button -->
                <button
                class="absolute top-1 right-2 text-gray-600 hover:text-black text-lg font-bold z-10" 
                on:click={close}>
                ✕
                </button>

                <!-- Event Image -->
                <div class="w-full canva-embed-code max-h-100 overflow-hidden rounded-md">
                    {@html event.detail.embed_code}
                </div>

                <!-- Event Title -->
                <h2 class="text-2xl text-blue-800 font-semibold mt-4">
                    {event.detail.title}
                </h2>

                <!-- Event Location & Time -->
                <div class="text-lg text-gray-700 mt-2 flex flex-col">
                    <p class="flex items-center">
                        📍 {event.detail.location}
                    </p>
                    <p>
                        📅 {getFormattedDateTime(event.detail.start_time, event.detail.end_time)}
                    </p>
                </div>

                <!-- Event Description -->
                <div class="text-gray-700 mt-3 text-sm leading-relaxed max-h-32 overflow-y-auto break-words">
                    {event.detail.description}
                </div>

                <!-- Buttons -->
                <div class="mt-6 flex space-x-4">
                    <button class="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        RSVP
                    </button>
                    <button class="flex-1 bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">
                        Sign In
                    </button>
                </div>
            </div>
        {/if}

        {#if layoutClass == "square"}
            <div class="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto flex flex-col">
                <!-- left side -->
                <div class="text-4xl blue-800 font-semibold pb-5">
                    <h2>{event.detail.title}</h2>
                </div>
                <div class="flex space-x-6">
                    <div class="w-1/2">
                        <!-- Event Time & Date + Location-->
                        <div class =" text-2xl black-600 font-semibold pb-3">
                            <p>{getFormattedDateTime(event.detail.start_time, event.detail.end_time)}</p>
                            <p>{event.detail.location}</p>
                        </div>

                        <!-- Event Description, prevents overflow on the x axis. Breaks Words-->
                        <div class="w-full max-w-md h-48 p-2 bg-gray-50 overflow-y-auto rounded-md whitespace-normal break-words -ml-0.5">
                            <p class=" black-600 font-normal leading-relaxed">{event.detail.description}</p>
                        </div>

                        <!-- Buttons -->
                        <div class="mt-6 flex-row justify-between space-x-4">
                            <button class="flex-1 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                                RSVP
                            </button>
                            <button class="flex-1 bg-gray-300 px-6 py-2 rounded hover:bg-gray-400">
                                Sign in
                            </button>
                            <button class="bg-gray-300 px-4 py-2 rounded mr-2" on:click={close}>
                                Close
                            </button>
                        </div>
                    </div>
                    <div class="w-1/2 canva-embed-code">
                        {@html event.detail.embed_code}
                    </div>
                </div>
            </div>
        {/if}
    </div>
{/if}
