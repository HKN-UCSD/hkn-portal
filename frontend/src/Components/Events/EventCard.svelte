<script>
    import { onMount } from 'svelte';
    import { getEvents } from "./eventstore";
    
    let events = [];
    let logo = "/static/Default_card_banner.png";

    //Filter and sort events(Only keep Upcoming Events in ascending order)
    function filterEvents(allEvents) {
    const currentDate = new Date();
    //Does not compare time other than the date(Event list last until the day end)
    currentDate.setHours(0,0,0,0);
    const filteredEvents = allEvents
        .filter(event => {
        const eventStartTime = new Date(event.start_time);
        eventStartTime.setHours(0,0,0,0)
            return eventStartTime >= currentDate;
        })
        //Sort event in start time 
        .sort((a, b) => {
        const startTimeA = new Date(a.start_time);
        const startTimeB = new Date(b.start_time);
            return startTimeA - startTimeB;
        });

        return filteredEvents;
    }

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
    
    onMount(async () => {
      // Fetch events from the API and wait for the promise to resolve
      const allEvents = await getEvents();
      events = filterEvents(allEvents).slice(0,10);
    });
</script>
  
<div class="event-list">
    {#each events as event}
      <div class="event-card">
        {#if event.embed_code}
          <div class="embed-code">
          {@html event.embed_code}
          </div>
        {:else}
          <img class="default-image" src={logo} alt="{event.title}">
        {/if}
        
        <div class="card-content">
          <h2 class="title"><a href={`/events/${event.pk}`}>{event.name}</a></h2>
          <p class="eventtime">{getFormattedDateTime(event.start_time, event.end_time)}</p>
          <p class="location">{event.location}</p>
        </div>
      </div>
    {/each}
</div>
  
<style>
   .event-list {
        display: flex;
        flex-direction: column; 
        align-items: center;
    }

    .embed-code :global(div) {
        margin:0 !important;
    }
    .event-card {
        border: 2px solid;
        border-color: #333;
        border-radius: 10px;
        overflow-x: hidden;
        overflow-y: hidden;
        padding: 0px;
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        border: 2px solid black;
        height: 280px;
        width: 300px;
        margin: 20px;
        scrollbar-width: none;
    }
    

    .embed-code{
        height:160px;
        object-fit: cover;
        object-position: top; 
        width: 100%;
        vertical-align: middle;
        overflow: hidden; 
        margin: 0; 
        padding: 0; 
    }
    .default-image {
        height:160px;
        object-position: top; 
        max-width: 100%;
        vertical-align: middle;
        overflow: hidden; 
        margin: 0; 
        padding: 0; 
    }
    .title a {
        color: black;
        font-size: 25px;
        text-decoration: none;
        margin: 0px 0px 0px 20px;
        display: inline-block;
    }

    .title a:hover {
        text-decoration: underline; /* Add underline on hover for links */
    }

    .card-content {
        margin:0px;
        width: 100%;
        text-align: left;
    }
    .eventtime{
        color: black;
        font-size: 14px;
        text-decoration: none;
        margin: 5px 0px 0px 20px;
    }

    .location{ 
        color: black;
        font-size: 14px;
        text-decoration: none;
        margin: 5px 0px 0px 20px;
        float: left;
    }


    h2{
        margin:12px 0px;
    }
</style>
  