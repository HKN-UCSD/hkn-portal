<script>
    import { onMount } from 'svelte';
    import { Calendar } from '@fullcalendar/core';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import listPlugin from '@fullcalendar/list';

    let calendarEl;

    onMount(() => {
        let calendar = new Calendar(calendarEl, {
            aspectRatio: 2,
            headerToolbar: {
                start: 'prev,next', // Add custom buttons here
                center: 'title',
                end: 'MonthButton,WeekButton,ListButton'
            },
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
            initialView: 'dayGridMonth',
            eventInteractive: true,
            events: [
                //Will figure out how to fetch event from server (Easy api call)
                { title: 'HKN test 1', start: '2023-10-01', url:'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
                { title: 'HKN test 2', start: '2023-10-10' },
            ],
            customButtons: {
            MonthButton: {
                text: 'Month', // Button text
                click: function () {
                    calendar.changeView('dayGridMonth'); // Change to dayGridMonth view
                }
            },
            WeekButton: {
                text: 'Week', // Button text
                click: function () {
                    calendar.changeView('timeGridWeek'); // Change to timeGridWeek view
                }
            },
            ListButton: {
                text: 'List', // Button text
                click: function () {
                    calendar.changeView('listMonth'); // Change to timeGridWeek view
                }
            }
            // Add more custom buttons as needed
        }
        });

        calendar.render();
    });
</script>

<div bind:this={calendarEl}></div>

