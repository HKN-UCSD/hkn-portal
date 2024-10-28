<script>
    import "./eventutils";
    import Modal from "./EditPointsModal.svelte";
    import { onMount, tick } from "svelte";
    import {
        requestAction,
        deleteAction,
        getAvailableSelfActions,
        addToCalendar,
        fetchEventTable,
        generateQRCode,
    } from "./eventutils";
    import EventRidesDisplay from "./EventRidesDisplay.svelte";
    export let event;
    let eventid = event.pk;
    let emailsCheckedOff = [];
    let emailsRsvp = [];

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

    let signed_in;
    let rsvpd;
    onMount(() => {
        fetchAllEventData();
    });

    // generate a console table
    let selectedProperties = ["Name", "Check Off", "Points", "Edit Points", "Sign In Time"];
    let hiddenProperties = ["Email"]
    filters = [(row) => row["Sign In Time"] != undefined];
  
    // TODO: Consider making a config file defining tables and their names/columns

    let csv_data;

    function tableToCSV() {

        // Variable to store the final csv data
        csv_data = [];

        // Get each row data
        var rows = document.getElementsByTagName('tr');
        var cols = rows[0].querySelectorAll('td,th');

        for (var i = 0; i < rows.length; i++) {

            // Get each column data
            cols = rows[i].querySelectorAll('td,th');

            // Stores each csv row data
            var csvrow = [];
            for (var j = 0; j < selectedProperties.length; j++) {
                if (typeof sortedRows[0][selectedProperties[j]] != "object") {
                    var data = "\"" + cols[j].innerHTML + "\"";
                    for (var k = 1; k < data.length - 1; k++) {
                        if (data.charAt(k) == "\"") {
                            data = data.slice(0,k) + "\"" + data.slice(k);
                            k++;
                        }
                    }
                    csvrow.push(data);
                } 
            }
            for (var j = 0; j < hiddenProperties.length; j++) {
                // no need to check for object because no point in having object as hidden property
                var data = "\"" + cols[j + selectedProperties.length].innerHTML + "\"";
                for (var k = 1; k < data.length - 1; k++) {
                    if (data.charAt(k) == "\"") {
                        data = data.slice(0,k) + "\"" + data.slice(k);
                        k++;
                    }
                }
                csvrow.push(data);
            }

            // Combine each column value with comma
            csv_data.push(csvrow.join(","));
        }

        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

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
    <p>Loading...</p>
{:else}
    <div class="selfactions">
        {#each selfActions as selfAction}
            {@const record = user.records.find(
                (record) => record.action == selfAction,
            )}
            <!-- If a record was found, provide a delete option; otherwise allow user
            to take the action -->
            {#if record == undefined}
                <button
                    on:click={() => {
                        return requestAction(event, selfAction, user).then(
                            (value) => fetchAllEventData(),
                            (reason) => fetchAllEventData(),
                        );
                    }}
                >
                    {selfAction}
                </button>
            {:else}
                <button
                    on:click={() => {
                        return deleteAction(record.pk).then(
                            (value) => fetchAllEventData(),
                            (reason) => fetchAllEventData(),
                        )}}
                >
                    un{selfAction}
                </button>
            {/if}
        {/each}
        <!--  add to calendar -->
        <button on:click={() => addToCalendar(event) }>
            Add to Calendar
        </button>
        <!--  generate qr code -->
        {#await checkAdmin()}
            <p>Loading...</p>
        {:then isAdmin}
            {#if isAdmin}
                <button on:click={() => generateQRCode(event) }>
                    Generate QR Code
                </button>
            {/if}
        {/await}
    </div>

    <EventRidesDisplay {event} />

    {#if isPageLoading}
       <p>Loading...</p>
    {:else if isAdmin}
        <h2>Event Console</h2>
        <div class="tab">
            <button
                class="tablinks"
                id="signed-in"
                bind:this={signed_in}
                selected="true"
                style:background-color={buttonBackgroundToggle
                    ? "var(--fc-button-bg-color)"
                    : "gray"}
                on:click={() => {
                    selectedProperties = [
                        "Name",
                        "Check Off",
                        "Points",
                        "Edit Points",
                        "Sign In Time",
                    ];
                    hiddenProperties = ["Email"]
                    filters = [(row) => row["Sign In Time"] != undefined];
                    if (!buttonBackgroundToggle) {
                        changeButtonColor();
                    }
                }}
            >
                Sign In List
            </button>
            <button
                class="tablinks"
                id="rsvpd"
                bind:this={rsvpd}
                selected="false"
                style:background-color={buttonBackgroundToggle
                    ? "gray"
                    : "var(--fc-button-bg-color)"}
                on:click={() => {
                    selectedProperties = ["Name", "Email", "RSVP Time"];
                    hiddenProperties = []
                    filters = [];
                    if (buttonBackgroundToggle) {
                        changeButtonColor();
                    }
                    }}>
                    RSVP List
            </button>
            <script>

            </script>
            <button 
                on:click={() => {
                    let rsvpd = document.getElementById("rsvpd");
                    if (rsvpd.selected) {
                        copyToClipboard(emailsRsvp, true);
                    } else {
                        copyToClipboard(emailsCheckedOff, false);
                    }
                }}>
                Copy Emails
            </button>
        </div>

        <table style="margin-top: 0px;">
            <thead>
                <tr>
                    {#each selectedProperties as property}
                        <th>{property}</th>
                    {/each}
                    {#each hiddenProperties as property}
                        <th class="hidden">{property}</th>
                    {/each}
                </tr>
            </thead>
            <tbody>
                {#each sortedRows as object (object.Id)}
                    <tr>
                        {#each selectedProperties as property}
                            {#if typeof object[property] == "object"}
                                <td>
                                    {#if object[property].text == "Edit Points" && object["Check Off Id"] == undefined}
                                        <button
                                            on:click={object[property].onclick.apply(
                                                null,
                                                object[property].args
                                            )}
                                            disabled="true"
                                            style="background-color: gray;"
                                        >
                                            {object[property].text}
                                        </button>
                                    {:else}
                                        <button
                                            on:click={() => {
                                                object[property].onclick.apply(
                                                    null,
                                                    object[property].args
                                                ).then(
                                                    (value) => fetchAllEventData(),
                                                    (reason) => fetchAllEventData()
                                                )
                                            }}
                                        >
                                            {object[property].text}
                                        </button>
                                    {/if}
                                </td>
                            {:else}
                                <td>{object[property] === undefined ? "N/A" : object[property]}</td>
                            {/if}
                        {/each}
                        {#each hiddenProperties as property}
                            <td class="hidden">{object[property] === undefined ? "N/A" : object[property]}</td>
                        {/each}
                    </tr>
                {/each}
            </tbody>
        </table>

        <button id="downloadButton" type="button" on:click={() => download_table()}>
            Download as CSV
        </button>

        {#if modalUserData}
            <Modal bind:modalUserData on:pointsEdited={fetchAllEventData}/>
        {/if}
    {/if}
{/if}

<style>
    table,
    th,
    td {
        border: none;
        border-collapse: collapse;
    }

    td {
        padding: 10px 15px;
    }

    th {
        padding: 15px;
        background-color: var(--fc-button-bg-color);
        color: white;
    }

    .selfactions {
        display: flex;
        flex-direction: row;
        gap: 10px;
    }

    .tab {
        margin-bottom: 0px;
    }

    .tablinks {
        margin-bottom: 0px;
        border-radius: 0px;
    }

    .hidden {
        display: none
    }
</style>
