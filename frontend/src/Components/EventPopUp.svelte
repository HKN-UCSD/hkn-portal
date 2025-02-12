<!-- src/Components/EventModal.svelte -->
<script>
    export let event = event;
    export let close;

    
    // If no event is provided, close the modal
    if (!event) {
        close(); // Close if no event is provided
    }
    
</script>

{#if event}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
        <div class="bg-white p-6 rounded-lg shadow-lg max-w-lg w-full">
            <h2 class="text-2xl font-bold">{event.detail.title}</h2>
            <p class="text-gray-600 mt-2">{event.detail.description}</p>
            <p class="text-gray-600 mt-2">{event.detail}</p>
            <div class="mt-4 flex justify-end">
                <button class="bg-gray-300 px-4 py-2 rounded mr-2" on:click={close}>Close</button>
            </div>
        </div>
    </div>
{/if}
