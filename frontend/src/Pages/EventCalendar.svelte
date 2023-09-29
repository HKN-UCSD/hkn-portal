<script>
    import { onMount } from 'svelte';
    import { Calendar } from '@fullcalendar/core';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';


    let calendarEl;

    onMount(() => {
        let calendar = new Calendar(calendarEl, {
            aspectRatio: 2,
            headerToolbar: {
                start: 'title prev,next',
                end: 'title'
            },
            plugins: [dayGridPlugin, timeGridPlugin],
            initialView: 'dayGridMonth',
            eventInteractive: true,
            events: [
                //Will figure out how to fetch event from server (Easy api call)
                { title: 'HKN test 1', start: '2023-09-01', url:'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
                { title: 'HKN test 2', start: '2023-09-10' },
            ],
        });

        calendar.render();
    });

    function changeView() {
    calendar.changeView('timeGridPlugin');
    }
</script>

<div bind:this={calendarEl}></div>

