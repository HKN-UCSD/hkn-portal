<script>
  import { onMount } from "svelte";
  import { getEvents } from "../Components/Events/eventstore";
  import Layout from "../Layout.svelte";
  import Cookies from "js-cookie";
  import EventsGrid from "../Components/Events/EventsGrid.svelte";
  import { eventGraphics } from "../Components/Events/EventGraphics";
  import EventCreateModal from "../Components/Events/EventCreateModal.svelte";
  import EventPopUp from "../Components/EventPopUp.svelte";
  let selectedEvent = null;
  let showPopup = false;
  let userData;
  let searchQuery = ""; // Stores search input
  let currentDate = new Date().toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  let closestEventID = null;
  let filters = {
    types: {
      technical: true,
      professional: true,
      outreach: true,
      social: true,
      mentorship: true,
      general: true,
    },
    when: {
      upcoming: true,
      past: false,
    },
  };

  const savedFilters = Cookies.get("eventFilters");
  if (savedFilters) {
    filters = JSON.parse(savedFilters);
  }

  function handleEventClick(event) {
    selectedEvent = event;
    showPopup = true; // Show popup when an event card is clicked
  }

  // Function to close the popup
  function closePopup() {
    showPopup = false;
  }

  export async function getPermissions() {
    let response = await fetch(`/api/permissions/`);
    return await response.json();
  }

  let allEvents = [];
  let filteredEvents = [];
  let allEventsUpcomingSorted = [];
  let allEventsPastSorted = [];


  async function getUserData() {
    try {
      const response = await fetch(`/api/profile/self/`);
      if (response.ok) {
        userData = await response.json();
      } else {
        console.error("Failed to fetch self data");
      }
    } catch (error) {
      console.error("Error fetching user data", error);
    }
  }

  async function fetchEvents() {
    await getUserData();
    const res = await getEvents();
    const curr = new Date().toISOString();

    allEvents = res.map((event) => ({
      title: event.name,
      description: event.description,
      pk: event.pk,
      location: event.location,
      url: `/events/${event.pk}`,
      type: event.event_type,
      start_time: event.start_time,
      end_time: event.end_time,
      embed_code: event.embed_code
        ? event.embed_code
        : eventGraphics[event.event_type],
      is_draft: event.is_draft,
      points: event.points,
      event_type: event.event_type,
    }));

    allEventsUpcomingSorted = [...allEvents]
    .filter(event => event.end_time > new Date().toISOString())
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));

    allEventsPastSorted = [...allEvents]
      .filter(event => event.start_time <= new Date().toISOString())
      .sort((a, b) => new Date(b.start_time) - new Date(a.start_time)); 


    allEvents.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));

    applyFilters();
  }

  function applyFilters() {
    
    let baseArray;

  if (filters.when.upcoming && !filters.when.past) {
    baseArray = allEventsUpcomingSorted;
  } else if (filters.when.past && !filters.when.upcoming) {
    baseArray = allEventsPastSorted;
  } else if (!filters.when.past && !filters.when.upcoming){
    baseArray = [];
  }else {
    baseArray = [...allEvents];
    baseArray.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
  }

  filteredEvents = baseArray
    .filter(event => filters.types[event.type.toLowerCase()] || false)
    .filter(event =>
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
    saveFiltersToCookies();
  }
  function saveFiltersToCookies() {
    Cookies.set("eventFilters", JSON.stringify(filters), {
      expires: 7,
      path: "",
    });
  }

  $: searchQuery, applyFilters();

  function selectAllTypes() {
    Object.keys(filters.types).forEach((type) => {
      filters.types[type] = true;
    });
    applyFilters();
  }

  function deselectAllTypes() {
    Object.keys(filters.types).forEach((type) => {
      filters.types[type] = false;
    });
    applyFilters();
  }

  function selectAllWhen() {
    Object.keys(filters.when).forEach((time) => {
      filters.when[time] = true;
    });
    applyFilters();
  }

  function deselectAllWhen() {
    Object.keys(filters.when).forEach((time) => {
      filters.when[time] = false;
    });
    applyFilters();
  }

  function deselectAllFilters() {
    Object.keys(filters).forEach((key) => {
      filters[key] = false;
    });
    applyFilters();
  }

  function selectAllFilters() {
    Object.keys(filters).forEach((category) => {
      Object.keys(filters[category]).forEach((key) => {
        filters[category][key] = true;
      });
    });
    applyFilters();
  }

  onMount(async () => {
    await fetchEvents();
    
    const handleKeydown = (event) => {
      if (event.key === "Escape") {
        closePopup();
      }
    };
    document.addEventListener("keydown", handleKeydown);

    closestEventID = getMostRecentEvent(allEvents);
    scrollToEvent(closestEventID);
  });

  let isModalOpen = false;

  function openModal() {
    isModalOpen = true;
  }

  function closeModal() {
    isModalOpen = false;
  }

  // Function to get the most recent event based on the current date
  function getMostRecentEvent(allEvents) {
    let closestEvent = null;
    let minDateDifference = Infinity;

    if (Array.isArray(allEvents))  {
        allEvents.forEach(event => {
        const eventStartDate = new Date(event.start_time).toISOString()
        const timeDifference = Math.abs(new Date(currentDate) - new Date(eventStartDate));  // Compare dates
        if (timeDifference <= minDateDifference) {
            minDateDifference = timeDifference;
            closestEvent = event.pk; // Store the ID of the closest event
        }
        });
    }
    return closestEvent;
  }

  // Function to scroll to the event with the given ID
  function scrollToEvent(eventID) {
    const eventElement = document.getElementById(`event-${eventID}`);
    const eventsGrid = document.getElementById('eventsgrid');
    if (eventsGrid && eventElement) {
    
    eventsGrid.scrollTo({
      top: eventElement.offsetTop - eventsGrid.offsetTop,
      behavior: 'smooth'
    });

    }
  }

</script>


<Layout>
  <div class="flex flex-col mt-10">
    <div class="flex flex-col md:flex-row mt-5 overflow-auto gap-7">
      <!-- Sidebar -->
      <div class="md:w-1/4 mb-5">
        <div
          class="bg-gray-50 active:bg-gray-100 border border-gray-300 rounded-xl shadow-md p-6"
        >
          <h2 class="text-xl font-semibold mb-4">Filter</h2>
          <!-- Search Bar -->
          <input
            type="text"
            bind:value={searchQuery}
            placeholder="Search events..."
            class="w-full p-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            on:input={applyFilters}
          />
          <hr class="my-4 border-gray-300" />

          <div class="flex justify-between items-center mt-4">
            <h3 class="font-semibold">Type</h3>
            <div class="flex gap-2 text-[10px]">
              <button
                class="text-gray-400 hover:underline cursor-pointer"
                on:click={selectAllTypes}>Select All</button
              >
              <p class="text-gray-400">|</p>
              <button
                class="text-gray-400 hover:underline cursor-pointer"
                on:click={deselectAllTypes}>Deselect All</button
              >
            </div>
          </div>

          <div class="space-y-2">
            {#each Object.keys(filters.types) as type}
              <label class="flex items-center">
                <input
                  type="checkbox"
                  bind:checked={filters.types[type]}
                  class="mr-2"
                  on:change={applyFilters}
                />
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </label>
            {/each}
          </div>

          <hr class="my-4 border-gray-300" />

          <div class="flex justify-between items-center mt-4">
            <h3 class="font-semibold">When</h3>
            <div class="flex gap-2 text-[10px]">
              <button
                class="text-gray-400 hover:underline cursor-pointer"
                on:click={selectAllWhen}>Select All</button
              >
              <p class="text-gray-400">|</p>
              <button
                class="text-gray-400 hover:underline cursor-pointer"
                on:click={deselectAllWhen}>Deselect All</button
              >
            </div>
          </div>
          <div class="space-y-2">
            {#each ["upcoming", "past"] as time}
              <label class="flex items-center">
                <input
                  type="checkbox"
                  bind:checked={filters.when[time]}
                  class="mr-2"
                  on:change={applyFilters}
                />
                {time.charAt(0).toUpperCase() + time.slice(1)} Events
              </label>
            {/each}
          </div>
        </div>
        {#await getPermissions()}
          <p>Loading...</p>
        {:then permissions}
          {#if permissions.is_admin}
            <button
              class="mt-4 w-full py-4 bg-secondary text-white font-semibold py-2 rounded-lg transition-all duration-300 transform hover:bg-primary"
              on:click={openModal}
            >
              Create Event
            </button>
            <EventCreateModal isOpen={isModalOpen} on:close={closeModal} />
          {/if}
        {:catch error}
          <p>Error: {error.message}</p>
        {/await}
      </div>

      {#if showPopup}
        <!-- Listens for the dispatch from close on EventPopUp -->
        <EventPopUp event={selectedEvent} on:close={closePopup} />
      {/if}
      <!-- Main Content -->
      <div id= "eventsgrid" class="md:w-3/4 bg-gray rounded-lg shadow-md mb-8 h-[80vh] overflow-auto">
        <EventsGrid
          title="Events"
          subtitle={currentDate}
          events={filteredEvents}
          {handleEventClick}
        />
      </div>
    </div>
  </div>
</Layout>
