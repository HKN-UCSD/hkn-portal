<script>
    import { createEventDispatcher, onMount } from "svelte";
    import { getFormData } from "../../Components/Events/eventutils";
    import { navigate } from "svelte-routing";

    export let idOfEventToEdit = undefined;
    export let isOpen = false;
    const dispatch = createEventDispatcher();


    let CSRFToken = document.cookie
        .split("; ")
        .find((element) => element.startsWith("csrftoken="))
        .split("=")[1];

    let searchTerm = "";

    let officers = [];
    let filteredHosts = [];
    let isDropdownOpen = false;  // Flag to control dropdown visibility
    let selectedHosts = [];

    // Function to filter hosts based on search term
    function filterHosts() {
        filteredHosts = officers.filter((option) => {
            const fullName = `${option.preferred_name} ${option.last_name} (${option.email})`.toLowerCase();
            return fullName.includes(searchTerm.toLowerCase());
        });
    }


    onMount(async () => {
    try {
      const data = await getFormData(idOfEventToEdit);
      officers = data.officers;
      filteredHosts = officers; // Initially, show all officers
      console.log('hosts', officers)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  });

    // Watch for changes in the search term and filter hosts accordingly
    $: searchTerm, filterHosts();

    function handleInputChange() {
        isDropdownOpen = true; // Open the dropdown

    }

    // Handle selecting a host
    function handleHostSelection(host) {
        console.log('Selected host:', host);
        if (!selectedHosts.some(h => h.email === host.email)) { // Prevent duplicates
            selectedHosts = [...selectedHosts, host]; // Add host to array
        }
        searchTerm = ''; // Clear the search input
        isDropdownOpen = false; // Close the dropdown
    }

    // Remove a host from selectedHosts
    function removeHost(hostToRemove) {
        selectedHosts = selectedHosts.filter(h => h.email !== hostToRemove.email);
    }
    // Function to handle input change


    function resetModalData() {
        // Reset any modal data or state that you want to clear
        searchTerm = "";
        isDropdownOpen = false;
        filteredHosts = []; // Or officers if you want to reset the list
        officers = [];
        isOpen = false;

    }

    function resetForm(form) {
        // Reset form fields manually
        form.reset();
        // If you have any custom fields that need to be reset (e.g., dropdowns, date pickers)
        searchTerm = ""; // Reset search term
        isDropdownOpen = false; // Reset dropdown visibility
        filteredHosts = []; // Reset filtered hosts if any
    }

    async function onSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        formData.set("csrfmiddlewaretoken", CSRFToken);

        const start_date_in_utc = new Date(
            formData.get("start_time")
        ).toISOString();
        const end_date_in_utc = new Date(
            formData.get("end_time")
        ).toISOString();

        if (start_date_in_utc >= end_date_in_utc) {
            alert(`Start Time needs to be before End Time`);
            return false;
        }



        formData.set("start_time", start_date_in_utc);
        formData.set("end_time", end_date_in_utc);
        formData.set("is_draft", !formData.get("is_ready"));
        selectedHosts.forEach(h => formData.append("hosts", h.user_id));
        formData.append("view_groups", 4)
        try {
            if (idOfEventToEdit == undefined) {
                const response = await fetch(`/api/events/`, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": CSRFToken,
                    },
                });

                if (!response.ok) {
                    alert(
                        `Unable to create event. Response status ${response.status}`
                    );
                } else {
                    alert("Successfully created event");
                    resetModalData();
                    resetForm(form);
                    navigate("/events");
                    window.location.reload(); // Refresh the page to reflect the changes
                }
            } else {
                const response = await fetch(`/api/events/${idOfEventToEdit}/`, {
                    method: "PUT",
                    body: formData,
                    headers: {
                        "X-CSRFToken": CSRFToken,
                    },
                });
                if (!response.ok) {
                    alert(
                        `Unable to edit event. Response status ${response.status}`
                    );
                } else {
                    navigate(`/events/${idOfEventToEdit}`);
                }
            }
        } catch (error) {
            alert(`Unable to create event. API error ${error}`);
        }
    }

    async function handleClose() {
        const confirmSave = confirm("Do you want to save this as a draft before closing?");
        if (confirmSave) {
            // Trigger form submission as a draft
            const form = document.querySelector('form'); // Get the form element
            const formData = new FormData(form);
            formData.set("is_draft", true);

            fetch(`/api/events/`, {
                method: idOfEventToEdit ? "PUT" : "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": CSRFToken,
                },
            })
            .then(response => {
                if (!response.ok) {
                    alert(`Unable to save draft. Response status ${response.status}`);
                } else {
                    alert("Draft saved successfully");
                    resetModalData();
                    resetForm(form);
                    navigate("/events");
                    dispatch("close");
                    window.location.reload();
                }
            })
            .catch(error => {
                alert(`Unable to save draft. API error ${error}`);
            });
        } else {
            // Just close the modal without saving
            dispatch("close");
        }
    }
</script>
{#if isOpen}
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 z-10" on:click={() => dispatch("close")}></div>

    <!-- Modal Container -->
    <div class="mt-2 fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-8 z-20 w-full max-w-3xl max-h-[85vh] overflow-auto rounded-xl shadow-2xl">

        <!-- Close Button -->
        <button class="absolute top-4 right-4 text-xl font-bold cursor-pointer text-gray-500 hover:text-gray-800 transition" on:click={() => handleClose()}>
            &times;
        </button>

        <!-- Title -->
        <h2 class="text-center text-3xl font-semibold text-primary mb-6">
            {idOfEventToEdit == undefined ? "Create Event" : "Edit Event"}
        </h2>

        {#await getFormData(idOfEventToEdit)}
            <p class="text-center text-gray-500">Loading...</p>
        {:then data}

        <!-- Form -->
        <form on:submit={onSubmit} class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-medium">Embed Code</label>
                    <input type="text" name="embed_code" id="id_embed_code" placeholder="Embed Code" value={data.eventToEdit.embed_code || ""} class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                    <label class="block text-gray-700 font-medium">Event Title *</label>
                    <input type="text" name="name" maxlength="255" required id="id_name" placeholder="Enter event title" value={data.eventToEdit.name || ""} class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
            </div>
            <div>
                <label class="block text-gray-700 font-medium">Event Type *</label>
                <select name="event_type" required id="id_event_type" class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                    <option value="" selected>Choose Event Type</option>
                    {#each data.eventTypes as option}
                        <option value={option.name} selected={data.eventToEdit.event_type && data.eventToEdit.event_type == option.name}>{option.name}</option>
                    {/each}
                </select>
            </div>
            <div>
                <label class="block text-gray-700 font-medium">Location</label>
                <input type="text" name="location" id="id_location" placeholder="Location" value={data.eventToEdit.location || ""} class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            <div>
                <label class="block text-gray-700 font-medium">Search for Host</label>
                <div class="flex flex-wrap border border-gray-300 rounded-md p-2">
                    <!-- Display selected hosts as removable tags -->
                    {#each selectedHosts as host}
                        <div class="bg-gray-200 px-2 py-1 m-1 rounded flex items-center">
                            {host.preferred_name} {host.last_name}
                            <button class="ml-2 text-red-500" on:click={() => removeHost(host)}>x</button>
                        </div>
                    {/each}
                    <!-- Search input -->
                    <input
                        type="text"
                        bind:value={searchTerm}
                        placeholder="Search for Host"
                        class="flex-grow p-1 outline-none bg-transparent"
                        on:input={handleInputChange}
                    />
                </div>
                <!-- Dropdown for host options -->
                {#if isDropdownOpen}
                    <ul class="mt-2 bg-white border border-gray-300 rounded-md shadow-lg">
                        {#each filteredHosts as option}
                            <li
                                name="host"
                                class="px-4 py-2 cursor-pointer hover:bg-gray-200"
                                on:click={() => handleHostSelection(option)}
                            >
                                {option.preferred_name} {option.last_name} ({option.email})
                            </li>
                        {/each}
                    </ul>
                {/if}
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-medium">Start Time *</label>
                    <input type="datetime-local" name="start_time" id="id_start_time" value={data.eventToEdit.start_time} class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                    <label class="block text-gray-700 font-medium">End Time *</label>
                    <input type="datetime-local" name="end_time" id="id_end_time" value={data.eventToEdit.end_time} class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
                </div>
            </div>
            <div>
                <label class="block text-gray-700 font-medium">Points</label>
                <input type="number" name="points" value={data.eventToEdit.points || 1} step="0.5" required id="id_points" placeholder="Points" class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" />
            </div>
            <div>
                <label class="block text-gray-700 font-medium">Event Description</label>
                <textarea name="description" id="id_description" rows="4" class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" placeholder="tell me about it!">{data.eventToEdit.description || ""}</textarea>
            </div>
            <div>
                <label class="block text-gray-700 font-medium">View Groups</label>
                <select name="view_groups" id="id_view_groups" multiple class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary">
                    <option value="1" selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(1)}>Inductee</option>
                    <option value="2" selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(2)}>Member</option>
                    <option value="3" selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(3)}>Outreach</option>
                </select>
            </div>
           <!-- Checkbox Section -->
           <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="flex items-center">
                <input type="checkbox" name="visible_to_guests" id="id_visible_to_guests" checked={data.eventToEdit.visible_to_guests} class="mr-2" />
                <label for="id_visible_to_guests" class="text-gray-700 font-medium">Visible to Guests</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" name="time_restricted" id="id_time_restricted" checked={data.eventToEdit.time_restricted} class="mr-2" />
                <label for="id_time_restricted" class="text-gray-700 font-medium">Time Restricted</label>
            </div>
            <div class="flex items-center">
                <input type="checkbox" name="is_ready" id="id_is_ready" checked={data.eventToEdit.is_ready} class="mr-2" />
                <label for="id_is_ready" class="text-gray-700 font-medium">Is Ready</label>
            </div>
        </div>
            <div class="text-center">
                <button type="submit" class="bg-secondary text-white py-3 px-6 rounded-md text-lg font-medium hover:bg-primary transition">Save Event</button>
            </div>
        </form>
        {/await}
    </div>
{/if}
