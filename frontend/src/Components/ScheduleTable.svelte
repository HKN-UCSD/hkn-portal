<script>
    export let days;
    export let timeslots;
</script>

<table class="mb-14 w-full h-full divide-y divide-gray-200 table-auto border-separate border-spacing-x-1 border-spacing-y-0.5">
    <thead>
        <tr>
            <th id="empty_for_time_column" class="w-10 px-2"></th> <!-- Empty header for the time column -->
            {#each days as day}
                <th class="w-12 lg:w-12 px-4 text-center">
                    <div class="flex items-center justify-center gap-2">
                        <span>{day}</span>
                    </div>
                </th>
            {/each}
        </tr>
    </thead>
    <tbody>
        {#each timeslots as time, slot_num}
            <tr class="h-4">
                <!-- Time column -->
                {#if time.includes("00")}
                    <td class="relative pr text-end items-start text-primary" rowspan=4>
                        <span class="absolute -top-1 right-1">{time}</span>
                    </td>
                {/if}
                <!-- Loop for days and generate cells -->
                {#each days as day, day_num}
                    <td id="{day_num}-{slot_num}"
                        class="h-4 w-12 lg:w-20 mx-1 px-4 text-center bg-unavailable timeslot">
                    </td>
                {/each}
            </tr>
        {/each}
    </tbody>
</table>