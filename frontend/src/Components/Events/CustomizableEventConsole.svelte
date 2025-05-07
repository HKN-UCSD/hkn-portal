<script>
    import "./eventutils";
    import Modal from "./EditPointsModal.svelte";
    import { onMount, tick } from "svelte";
    import {
        getAvailableSelfActions,
        fetchEventTable,
    } from "./eventutils";
    import EventRidesDisplay from "./EventRidesDisplay.svelte";
    import { navigate } from "svelte-routing";
    import EventCreateModal from "./EventCreateModal.svelte"


    export let event;
    export let time;
    export let date;

    let eventid = event.pk;
    let emailsCheckedOff = [];
    let emailsRsvp = [];

    async function onDelete() {
        const isConfirmed = window.confirm("Are you sure you want to delete this event?");
        if (isConfirmed) {
            try {
                const response = await fetch(`/api/events/${eventid}/`, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": document.cookie
                            .split("; ")
                            .find((element) => element.startsWith("csrftoken="))
                            .split("=")[1],
                    },
                });

                if (!response.ok) {
                    alert(
                        `Unable to delete event. Response status ${response.status}`
                    );
                } else {
                    alert("Successfully deleted event");
                    navigate("/");
                }
            } catch (error) {
                alert(`Unable to delete event. API error ${error}`);
            }
        }
    }

    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then((value) =>
            value.json(),
        );
        return response.is_admin;
    }

    // obtain user data
    async function getSelfUser(event) {
        let response = await fetch(`/api/users/self/`);
        if (response.status === 200) {
            let user = await response.json();
            let userRecordResponse = await fetch(
                `/api/eventactionrecords/pair/${event}/${user.user_id}/`,
            );
            let userRecord = await userRecordResponse.json();
            user["records"] = userRecord;
            return user;
        } else {
            throw new Error(response.statusText);
        }
    }
    
    async function copyToClipboard(text, rsvpd_tab) {
        if(text.length == 0){
            alert("No checked off attendees!");
        }else{
            if(rsvpd_tab){
                try {
                    await navigator.clipboard.writeText(text);
                    alert("RSVP'd attendee's email copied to clipboard!");
                } catch (err) {
                    console.error("Failed to copy:", err);
                    alert("Failed to copy text to clipboard.");
            }
            }else{
                try {
                    await navigator.clipboard.writeText(text);
                    alert("Checked-Off attendee's email copied to clipboard!");
                } catch (err) {
                    console.error("Failed to copy:", err);
                    alert("Failed to copy text to clipboard.");
                }
            }
            
        }
    }

    let editOpen = false;
    // Controls opening and closing of events edit
    function openModal() {
        editOpen = true;
    }

    function closeModal() {
        editOpen = false;
    }

    // This variable is used by the EditPointsModal to select a particular user
    // and edit that user's points. It is set to one of the rows of the table
    // during the Edit Points button on:click event.
    let modalUserData = false;

    // Filter Table
    let indexedRows = new Map();
    let isPageLoading = true;
    let selfActions = [];
    let isAdmin = false;
    let user = {};

    let filters = [];
    $: sortedRows = [...indexedRows.values()]
        .filter((row) => {
            for (let filter of filters) {
                if (!filter(row)) {
                    return false;
                }
            }
            return true;
        })
        .sort();

    let buttonBackgroundToggle = true;
    let changeButtonColor = () => {
        buttonBackgroundToggle = !buttonBackgroundToggle;
    };

    const fetchAllEventData = async () => {
        try {
            // Call your asynchronous function that returns a promise
            indexedRows = await fetchEventTable(event);
            emailsRsvp = [];
            indexedRows.forEach((row) => {
                if (row["RSVP Id"] !== undefined) {
                    emailsRsvp.push(row["Email"]);
                }
            });
            emailsCheckedOff = [];
            indexedRows.forEach((row) => {
                if (row["Check Off Id"] !== undefined) {
                    emailsCheckedOff.push(row["Email"]);
                }
            });

            // add the edit points button.
            indexedRows.forEach((row) => {
                row["Edit Points"] = {
                    onclick: async () => {
                        modalUserData = row;
                    },
                    text: "Edit Points",
                    args: [],
                };
            });

            user = await getSelfUser(eventid);
            isAdmin = await checkAdmin();
            selfActions = await getAvailableSelfActions(eventid);

            isPageLoading = false;
        } catch (error) {
            console.error("Error fetching table data:", error);
        }
    };

    onMount(() => {
        fetchAllEventData();
    });

    // generate a console table
    let selectedProperties = ["Name", "Check Off", "Points", "Edit Points", "Sign In Time"];
    let hiddenProperties = ["Email"]
    filters = [(row) => row["Sign In Time"] != undefined];
  
    // TODO: Consider making a config file defining tables and their names/columns

    let csv_data = [];
    function tableToCSV() {
        csv_data.push(`${event.title}, ${time}, ${date}`);
        if (!sortedRows || sortedRows.length === 0) {
                console.warn("[CSV] No data rows found in sortedRows.");
            return;
        }
        sortedRows.forEach(row => {
            let csvrow = [];

            selectedProperties.forEach(key => {
                let val = row[key];

                // If it's a button-like object, skip or grab text
                if (typeof val === "object" && val !== null && val.text !== undefined) {
                    csvrow.push(`"${val.text}"`);
                } else {
                    csvrow.push(`"${val !== undefined ? val : ""}"`);
                }
            });

            hiddenProperties.forEach(key => {
                csvrow.push(`"${row[key] !== undefined ? row[key] : ""}"`);
            });

            csv_data.push(csvrow.join(","));
        });

        csv_data = csv_data.join("\n");
    }


    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'inductees.csv';
        hiddenElement.click();
    }

    filters = [(row) => row["Sign In Time"] != undefined];

</script>

<!-- Event Action Bar -->
{#if isPageLoading}
    <!-- p class="text-center text-gray-600">Loading...</p -->
{:else}
    <EventRidesDisplay {event} />

    {#if isAdmin}
        <div>
            <div class="flex flex-wrap gap-4 space-x-4 items-center justify-center">
                <button class="text-white px-4 py-2 rounded"
                    class:bg-primary={!buttonBackgroundToggle}
                    class:bg-secondary={buttonBackgroundToggle}
                    on:click={() => {
                        if (!buttonBackgroundToggle) {
                            selectedProperties = ["Name", "Check Off", "Points", "Edit Points", "Sign In Time"];
                            hiddenProperties = ["Email"];
                            filters = [(row) => row["Sign In Time"] !== undefined];
                            changeButtonColor();
                        }
                    }}>
                    Sign In List
                </button>
                <button class="text-white px-4 py-2 rounded"
                    class:bg-primary={buttonBackgroundToggle}
                    class:bg-secondary={!buttonBackgroundToggle}
                    on:click={() => {
                        if (buttonBackgroundToggle) {
                            selectedProperties = ["Name", "Email", "RSVP Time"];
                            hiddenProperties = [];
                            filters = [];
                            changeButtonColor();
                        }
                    }}>
                    RSVP List
                </button>
                <button class="bg-primary text-white px-4 py-2 rounded"
                    on:click={() => copyToClipboard(buttonBackgroundToggle ? emailsCheckedOff : emailsRsvp, !buttonBackgroundToggle)}>
                    Copy Emails
                </button>

                <button class="bg-primary text-white px-4 py-2 rounded"
                    on:click={download_table}>
                    Download as CSV
                </button>
            </div>

            
            <table class="mt-4 border-collapse w-full shadow-md rounded-lg">
                <thead class="bg-gray-200">
                    <tr>{#each selectedProperties as property}<th class="p-3">{property}</th>{/each}</tr>
                </thead>
                <tbody>
                    {#each sortedRows as object (object.Id)}
                        <tr class="border-b">
                            {#each selectedProperties as property}
                                {#if typeof object[property] == "object"}
                                    <td class="p-3">
                                        {#if object[property].text == "Edit Points" && object["Check Off Id"] == undefined}
                                            <button class="bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed"
                                                disabled>
                                                {object[property].text}
                                            </button>
                                        {:else}
                                            <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
                                                on:click={() => object[property].onclick.apply(null, object[property].args)
                                                    .then(fetchAllEventData) }>
                                                {object[property].text}
                                            </button>
                                        {/if}
                                    </td>
                                {:else}
                                    <td class="p-3">{object[property] === undefined ? "N/A" : object[property]}</td>
                                {/if}
                            {/each}
                        </tr>
                    {/each}
                </tbody>
            </table>

            <div class = "flex space-x-4 items-center justify-center pt-6">
                {#if event.event_type == "Outreach"}
                    <button
                        class="bg-primary text-white px-4 py-2 rounded"
                        on:click={() => navigate(`/events/rides/${eventid}`)}>
                    Assign Rides
                    </button>
                {/if}
                <button
                    class="bg-primary text-white px-4 py-2 rounded"
                    on:click={openModal}>
                Edit
                </button>
                <EventCreateModal isOpen={editOpen} idOfEventToEdit={eventid} on:close={closeModal} />
                <button class="bg-red-500 text-white px-4 py-2 rounded"
                    on:click={onDelete}>Delete
                </button>
            </div>

            {#if modalUserData}
                <Modal bind:modalUserData on:pointsEdited={fetchAllEventData}/>
            {/if}
        </div>
    {/if}
{/if}
