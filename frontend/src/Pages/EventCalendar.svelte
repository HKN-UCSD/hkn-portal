<script>
    import { onMount } from 'svelte';
    import { Calendar } from '@fullcalendar/core';
    import dayGridPlugin from '@fullcalendar/daygrid';

    let calendarEl;

    onMount(() => {
        let calendar = new Calendar(calendarEl, {
            plugins: [dayGridPlugin],
            initialView: 'dayGridMonth',
            events: [
                //Will figure out how to fetch event from server (Easy api call)
                { title: 'HKN test 1', start: '2023-09-01' },
                { title: 'HKN test 2', start: '2023-09-10' },
            ],
        });

        calendar.render();
    });
</script>

<div bind:this={calendarEl}></div>

