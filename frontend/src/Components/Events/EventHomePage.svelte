<script>
    import { onMount } from 'svelte';
    import { Calendar } from '@fullcalendar/core';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import listPlugin from '@fullcalendar/list';
    import {getEvents } from "./eventstore";
    import { buildElAttrs } from '@fullcalendar/core/internal';
    let calendar;

    onMount(async () => {
        const calendarEl = document.getElementById('calendar');

        // Fetch events from the API and wait for the promise to resolve
        let events = await getEvents();

        calendar = new Calendar(calendarEl, {
            aspectRatio: 2,
            headerToolbar: {
                start: 'prev,next',
                center: 'title',
                end: 'MonthButton,WeekButton,ListButton'
            },
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
            initialView: 'dayGridMonth',
            eventInteractive: true,
            events: events.map(event => ({
                title: event.name,
                start: event.start_time,
                end:event.end_time,
                url: `http://localhost:8000/events/${event.pk}`,
                content: event.descriptions,
            })),
            eventColor: '#4350AF',
            customButtons: {
                MonthButton: {
                    text: 'Month',
                    click: function () {
                        calendar.changeView('dayGridMonth');
                    }
                },
                WeekButton: {
                    text: 'Week',
                    click: function () {
                        calendar.changeView('timeGridWeek');
                    }
                },
                ListButton: {
                    text: 'List',
                    click: function () {
                        calendar.changeView('listMonth');
                    }
                }
            }
        });

        calendar.render();
    });
</script>

<div id="calendar"></div>
