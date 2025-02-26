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

    // Function to filter hosts based on search term
    function filterHosts() {
        filteredHosts = officers.filter((option) => {
            const fullName = `${option.first_name} ${option.last_name} (${option.email})`.toLowerCase();
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

    function handleHostSelection(host) {
        console.log('Selected host:', host);
        searchTerm = `${host.first_name} ${host.last_name} (${host.email})`;  // Save selected host
        isDropdownOpen = false;  // Close the dropdown
    }

    // Function to handle input change
    function handleInputChange() {
        isDropdownOpen = true;  // Show dropdown on input change
    }

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
        formData.set("is_draft", !formData.get("is_draft"));

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
</script>

{#if isOpen}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="fixed top-0 left-0 w-full h-full bg-black bg-opacity-50 z-10" on:click={() => dispatch("close")}></div>
    <div class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-6 z-20 w-full max-w-4xl max-h-[80vh] overflow-auto rounded-lg">
        <button class="absolute top-2 right-2 text-xl font-bold cursor-pointer" on:click={() => dispatch("close")}>X</button>
        <h2 class="text-center text-2xl mb-5">{idOfEventToEdit == undefined ? "Create Event" : "Edit Event"}</h2>
        
        {#await getFormData(idOfEventToEdit)}
            <p>Loading...</p>
        {:then data}
        
        <form on:submit={onSubmit}>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Left Column: Embed Code -->
                <div class="mb-5">
                    <input
                        type="text"
                        name="embed_code"
                        id="id_embed_code"
                        placeholder="Embed Code"
                        value={data.eventToEdit.embed_code || ""}
                        class="w-full p-2 border border-gray-300 rounded-md"
                    />
                </div>

                <!-- Right Column: Everything Else -->
                <div>
                    <div class="mb-5">
                        <input
                            type="text"
                            name="name"
                            maxlength="255"
                            required
                            id="id_name"
                            placeholder="Name"
                            value={data.eventToEdit.name || ""}
                            class="w-full p-2 border border-gray-300 rounded-md"
                        />
                    </div>
                    <div class="mb-5">
                        <select name="event_type" required id="id_event_type" class="w-full p-2 border border-gray-300 rounded-md">
                            <option value="" selected>Event Type</option>
                            {#each data.eventTypes as option}
                                <option
                                    value={option.name}
                                    selected={data.eventToEdit.event_type &&
                                        data.eventToEdit.event_type ==
                                            option.name}>{option.name}</option>
                            {/each}
                        </select>
                    </div>
                    <div class="mb-5">
                        <input
                            type="text"
                            name="location"
                            maxlength="255"
                            id="id_location"
                            placeholder="Location"
                            value={data.eventToEdit.location || ""}
                            class="w-full p-2 border border-gray-300 rounded-md"
                        />
                    </div>
                    <div class="mb-5">
                        <input 
                        type="text" 
                        bind:value={searchTerm} 
                        placeholder="Search for Host" 
                        class="w-full p-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        on:input={handleInputChange}/>

                        {#if isDropdownOpen && filteredHosts.length > 0}
                            <ul class="mt-2 bg-white border border-gray-300 rounded-md">
                                {#each filteredHosts as option}
                                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                                    <li class="px-4 py-2 cursor-pointer hover:bg-gray-200"
                                        on:click={() => handleHostSelection(option)}>
                                        {option.preferred_name} {option.last_name} ({option.email})
                                    </li>
                                {/each}
                            </ul>
                       
                        {/if}
                    </div>
                    <div class="mb-5">
                        <input
                            type="datetime-local"
                            name="start_time"
                            id="id_start_time"
                            placeholder="Start Time"
                            value={data.eventToEdit.start_time}
                            class="w-full p-2 border border-gray-300 rounded-md"
                        />
                    </div>
                    <div class="mb-5">
                        <input
                            type="datetime-local"
                            name="end_time"
                            id="id_end_time"
                            placeholder="End Time"
                            value={data.eventToEdit.end_time}
                            class="w-full p-2 border border-gray-300 rounded-md"
                        />
                    </div>
                    <div class="mb-5">
                        <input
                            type="number"
                            name="points"
                            value={data.eventToEdit.points || 1}
                            step="0.5"
                            required
                            id="id_points"
                            placeholder="Points"
                            class="w-full p-2 border border-gray-300 rounded-md"
                        />
                    </div>
                    <div class="mb-5">
                        <textarea
                            name="description"
                            cols="40"
                            rows="10"
                            id="id_description"
                            placeholder="Description"
                            class="w-full p-2 border border-gray-300 rounded-md">{data.eventToEdit.description}</textarea>
                    </div>
                    <div class="mb-5">
                        <label for="id_view_groups">View Groups:</label>
                        <select name="view_groups" id="id_view_groups" multiple class="w-full p-2 border border-gray-300 rounded-md">
                            <option
                                value="1"
                                selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(1)}
                            >inductee</option>
                            <option
                                value="2"
                                selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(2)}
                            >member</option>
                            <option
                                value="3"
                                selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(3)}
                            >outreach</option>
                            <option
                                value="4"
                                selected={data.eventToEdit.view_groups && data.eventToEdit.view_groups.includes(4)}
                            >officer</option>
                        </select>
                    </div>
                    <div class="mb-5">
                        <label for="id_anon_viewable">Visible to guests:</label>
                        <input
                            type="checkbox"
                            name="anon_viewable"
                            id="id_anon_viewable"
                            checked={data.eventToEdit.anon_viewable !== undefined ? data.eventToEdit.anon_viewable : false}
                            class="p-2"
                        />
                    </div>
                    <div class="mb-5">
                        <label for="id_is_time_restricted">Time restricted:</label>
                        <input
                            type="checkbox"
                            name="is_time_restricted"
                            id="id_is_time_restricted"
                            checked={data.eventToEdit.is_time_restricted !== undefined ? data.eventToEdit.is_time_restricted : true}
                            class="p-2"
                        />
                    </div>
                    <div class="mb-5">
                        <label for="id_is_draft">Mark event as ready:</label>
                        <input
                            type="checkbox"
                            name="is_draft"
                            id="id_is_draft"
                            checked={data.eventToEdit.is_draft !== undefined ? !data.eventToEdit.is_draft : false}
                            class="p-2"
                        />
                    </div>
                    <input type="submit" value="Save" class="bg-primary text-white py-2 px-4 rounded-md cursor-pointer mt-5" />
                </div>
            </div>
        </form>
        {/await}
    </div>
{/if}
