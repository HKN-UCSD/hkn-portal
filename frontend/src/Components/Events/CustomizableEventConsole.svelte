<script>
    import "./eventutils";
    import Modal from "./EditPointsModal.svelte";
    import { onMount } from "svelte";
    import {
        requestAction,
        deleteAction,
        getAvailableOtherActions,
        getAvailableSelfActions,
        addToCalendar,
    } from "./eventutils";
    import EventRidesDisplay from "./EventRidesDisplay.svelte";
    export let event;
    let eventid = event.pk;
    let emailsCheckedOff = [];

    async function checkAdmin() {
        let response = await fetch(`/api/permissions/`).then(value => value.json());
        return response.is_admin;

    }

    // obtain user data
    async function getSelfUser(event) {
        let response = await fetch(`/api/users/self/`);
        if (response.status === 200) {
            let user = await response.json();
            let userRecordResponse = await fetch(`/api/eventactionrecords/pair/${event}/${user.user_id}/`);
            let userRecord = await userRecordResponse.json();
            user["records"] = userRecord;
            return user;
        } else {
            throw new Error(response.statusText);
        }
    }

    // This variable is used by the EditPointsModal to select a particular user
    // and edit that user's points. It is set to one of the rows of the table
    // during the Edit Points button on:click event.
    let modalUserData = false;

    // Event Console Table Setup

    // get all records related to an event
    async function generateTable() {
        let rows = new Map();

        // obtain all information necessary for the action bar and console table.
        let actionRecords, relatedUsers, otherActions;
        [actionRecords, relatedUsers, otherActions] = await Promise.all([
            fetch(`/api/eventactionrecords/?eventid=${eventid}`).then((value) =>
                value.json(),
            ),
            fetch(`/api/users/?eventid=${eventid}`).then((value) =>
                value.json(),
            ),
            getAvailableOtherActions(),
        ]);

        // For each action record, update/create rows describing user activity
        actionRecords.forEach((actionRecord) => {
            const userId = actionRecord["acted_on"];
            let row = rows.get(userId);
            if (!row) {
                row = { Points: 0 };
                rows.set(userId, row);
            }
            row[actionRecord["action"] + " Time"] = new Date(
                actionRecord["action_time"],
            ).toLocaleString();
            row[actionRecord["action"] + " Id"] = actionRecord["pk"]; // storing a record's id is necessary for deleting action records
            row["Points"] += actionRecord["points"];

            // remember the action records's id and that it is associated with this user and this action,
            // so that when generating buttons, we can trigger an un-delete.
        });

        // for each user, update its relevant row with email and name
        relatedUsers.forEach((user) => {
            const userId = user["user_id"];
            const row = rows.get(userId);
            if (row) {
                row["Name"] = `${user["preferred_name"]} ${user["last_name"]}`;
                row["Email"] = user["email"];
                row["Id"] = user["user_id"];
            }
        });
        
        rows.forEach((row) => {
            if (row["Check Off Id"] !== undefined) {
                emailsCheckedOff.push(row["Email"]);
            }
        });

        // for each row, add otherAction buttons (Not RSVP or Sign In)
        rows.forEach((row) => {
            otherActions.forEach((actionName) => {
                if (row[actionName + " Time"] == undefined) {
                    row[actionName] = {
                        // TODO: Make requestAction just take the event id instead of
                        // a whole event object. It's sooo uglyyy rn
                        onclick: requestAction,
                        text: actionName,
                        args: [
                            event,
                            actionName,
                            { user_id: row["Id"] },
                        ],
                    };
                } else {
                    row[actionName] = {
                        onclick: deleteAction,
                        text: "un-" + actionName,
                        args: [row[actionName + " Id"]],
                    };
                }
            });
            // special case the edit points button.
            row["Edit Points"] = {
                onclick: () => {
                    modalUserData = row;
                },
                text: "Edit Points",
                args: [],
            };
        });

        return rows;
    }

    async function copyToClipboard(text) {
        if(text.length == 0){
            alert("No checked off attendees!");
        }else{
            try {
                await navigator.clipboard.writeText(text);
                alert("Text copied to clipboard!");
            } catch (err) {
                console.error("Failed to copy:", err);
                alert("Failed to copy text to clipboard.");
            }
        }
    }

    // Filter Table
    let generateTablePromise = generateTable();
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

    onMount(async () => {
        try {
        // Call your asynchronous function that returns a promise
        let rows = await generateTable();
        user = await getSelfUser(eventid);
        isAdmin = await checkAdmin();
        selfActions = await getAvailableSelfActions(eventid);

        indexedRows = new Map(rows);
        isPageLoading = false;
        } catch (error) {
        console.error('Error fetching table data:', error);
        }
    });

    // generate a console table
    let selectedProperties = ["Name", "Email", "Check Off", "Points", "Edit Points", "Sign In Time"];
    filters = [(row) => row["Sign In Time"] != undefined];

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
            for (var j = 0; j < cols.length; j++) {
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

</script>

<!-- Event Action Bar -->
{#if isPageLoading}
    <p>Loading...</p>
{:else}
    <div class="selfactions">
        {#each selfActions as selfAction}
            {@const record = user.records.find((record) => record.action == selfAction)}
            <!-- If a record was found, provide a delete option; otherwise allow user
            to take the action -->
            {#if record == undefined}
                <button on:click={() => requestAction(event, selfAction, user)}>
                    {selfAction}
                </button>
            {:else}
                <button on:click={() => deleteAction(record.pk)}>
                    un{selfAction}
                </button>
            {/if}
        {/each}
        <!--  add to calendar -->
        <button on:click={() => addToCalendar(event) }>
            Add to Calendar
        </button>
    </div>

    <EventRidesDisplay {event} />

    {#if isPageLoading}
        <p>Loading...</p>
    {:else}
        {#if isAdmin}
            <h2>Event Console</h2>
            <div class="tab">
                <button
                    class="tablinks"
                    id="signed-in"
                    selected="true"
                    style:background-color= {buttonBackgroundToggle ? 'var(--fc-button-bg-color)' : 'gray'}
                    on:click={() => {
                        selectedProperties = ["Name", "Email", "Check Off", "Points", "Edit Points", "Sign In Time"];
                        filters = [(row) => row["Sign In Time"] != undefined];
                        if (!buttonBackgroundToggle) {changeButtonColor()};
                    }}>
                    Sign In List
                </button>
                <button
                    class="tablinks"
                    id="rsvpd"
                    selected="false"
                    style:background-color= {buttonBackgroundToggle ? 'gray' : 'var(--fc-button-bg-color)'}
                    on:click={() => {
                        selectedProperties = ["Name", "Email", "RSVP Time"];
                        filters = [];
                        if (buttonBackgroundToggle) {changeButtonColor()};

                    }}>
                    RSVP List
                </button>
              <button on:click={() => copyToClipboard(emailsCheckedOff)}>Copy Emails</button>
            </div>

            <table style="margin-top: 0px;">
                <tr>
                    {#each selectedProperties as property}
                        <th>{property}</th>
                    {/each}
                </tr>
                {#each sortedRows as object}
                    <tr>
                        {#each selectedProperties as property}
                            {#if typeof object[property] == "object"}
                                <td>
                                    {#if object[property].text == "Edit Points" & object["Check Off Id"] == undefined}
                                        <button
                                            on:click={object[property].onclick.apply(
                                                null,
                                                object[property].args,
                                            )}
                                            disabled="true"
                                            style="background-color: gray;"
                                            >
                                            {object[property].text}
                                        </button>
                                    {:else}
                                        <button
                                            on:click={object[property].onclick.apply(
                                                null,
                                                object[property].args,
                                            )}
                                            >
                                            {object[property].text}
                                        </button>
                                    {/if}
                                </td>
                            {:else}
                                <td>{object[property] === undefined ? "N/A" : object[property]}</td>
                            {/if}
                        {/each}
                    </tr>
                {/each}
            </table>

            <button id="downloadButton" type="button" on:click={() => download_table()}>
                Download as CSV
            </button>

            {#if modalUserData}
                <Modal bind:modalUserData />
            {/if}
        {/if}
    {/if}
    <Modal bind:modalUserData />
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
</style>
