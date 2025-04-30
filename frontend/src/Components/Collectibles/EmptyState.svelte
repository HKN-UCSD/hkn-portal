<script>
    export let message = "No items found";
    export let subtext = "Try adjusting your filters to see more items.";
    export let icon = "🔍";
</script>

<div class="flex flex-col items-center justify-center py-12 px-4 bg-gray-50 rounded-xl border border-gray-200">
    <div class="text-4xl mb-4">{icon}</div>
    <h3 class="text-xl font-semibold text-gray-700 mb-2">{message}</h3>
    <p class="text-gray-500 text-center max-w-md">{subtext}</p>
</div> 