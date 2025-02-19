<script>
    export let event;
    import { createEventDispatcher } from "svelte";
    
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
</script>

{#if event}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto flex flex-col">
            <!-- left side -->
            <div class="text-4xl text-blue-800 font-semibold pb-5">
                <h2>{event.detail.title}</h2>
            </div>
            <div class="flex space-x-6">
                <div class="w-1/2">
                    <!-- Event Time & Date + Location-->
                    <div class =" text-2xl text-black-600 font-semibold pb-3">
                        <p>{getFormattedDateTime(event.detail.start_time, event.detail.end_time)}</p>
                        <p>{event.detail.location}</p>
                    </div>

                    <!-- Event Description -->
                    <p class=" text-black-600 font-normal leading-relaxed scroll-box">{event.detail.description}</p>

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
    </div>  
{/if}
