<script>
    import { onMount } from 'svelte';
    import { Calendar } from '@fullcalendar/core';
    import dayGridPlugin from '@fullcalendar/daygrid';
    import timeGridPlugin from '@fullcalendar/timegrid';
    import listPlugin from '@fullcalendar/list';
    import {getEvents } from "./eventstore";
    import { navigate } from 'svelte-routing';
    let calendar;

    onMount(async () => {
        const calendarEl = document.getElementById('calendar');

        var eventColors = {
            'General': '#216CDE',
            'Mentorship': '#216CDE',
            'Professional': '#216CDE',
            'Technical': '#216CDE',
            'Social': '#216CDE',
            'Outreach': '#06402B',
        }

        // Fetch events from the API and wait for the promise to resolve
        let events = await getEvents();

        calendar = new Calendar(calendarEl, {
            aspectRatio: 2,
            headerToolbar: {
                start: 'today prev,next',
                center: 'title',
                end: 'MonthButton,WeekButton,ListButton'
            },
            eventClick: (info) => {
                info.jsEvent.preventDefault();
                navigate(info.event.url);
            },
            plugins: [dayGridPlugin, timeGridPlugin, listPlugin],
            initialView: 'dayGridMonth',
            eventInteractive: true,
            events: events.map(event => ({
                title: event.name,
                start: event.start_time,
                end: event.end_time,
                url: `/events/${event.pk}`,
                content: event.descriptions,
                backgroundColor: event.is_draft ? '#bababa' : eventColors[event.event_type],
                borderColor: event.is_draft ? '#bababa' : eventColors[event.event_type],
                textColor: '#FFFFFF',
            })),
            eventDisplay: 'block',
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
                        calendar.changeView('listYear');
                    }
                }
            }
        });

        calendar.render();
    });
</script>

<div id="calendar"></div>
