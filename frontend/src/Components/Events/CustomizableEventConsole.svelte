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
    } from "./eventutils";
    import EventRidesDisplay from "./EventRidesDisplay.svelte";
    export let event;
    let eventid = event.pk;
    let emailsCheckedOff = [];

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

    // This variable is used by the EditPointsModal to select a particular user
    // and edit that user's points. It is set to one of the rows of the table
    // during the Edit Points button on:click event.
    let modalUserData = false;

    // Event Console Table Setup

    // get all records related to an event

    async function copyToClipboard(text) {
        if (text.length == 0) {
            alert("No checked off attendees!");
        } else {
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
            console.log(indexedRows);

            user = await getSelfUser(eventid);
            isAdmin = await checkAdmin();
            selfActions = await getAvailableSelfActions(eventid);

            isPageLoading = false;
        } catch (error) {
            console.error("Error fetching table data:", error);
        }
    };

    onMount(fetchAllEventData);

    // generate a console table
    let selectedProperties = [
        "Name",
        "Check Off",
        "Points",
        "Edit Points",
        "Sign In Time",
    ];
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
        <button on:click={() => addToCalendar(event)}> Add to Calendar </button>
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
                selected="false"
                style:background-color={buttonBackgroundToggle
                    ? "gray"
                    : "var(--fc-button-bg-color)"}
                on:click={() => {
                    selectedProperties = ["Name", "Email", "RSVP Time"];
                    filters = [];
                    if (buttonBackgroundToggle) {
                        changeButtonColor();
                    }
                }}
            >
                RSVP List
            </button>
            <button on:click={() => copyToClipboard(emailsCheckedOff)}
                >Copy Emails</button
            >
        </div>

        <table style="margin-top: 0px;">
            <tr>
                {#each selectedProperties as property}
                    <th>{property}</th>
                {/each}
            </tr>
            {#key sortedRows}
            {#each sortedRows as object}
                <tr>
                    {#each selectedProperties as property}
                        {#if typeof object[property] == "object"} <!-- object properties indicate buttons/interactables -->
                            <td>
                                {#if (object[property].text == "Edit Points") & (object["Check Off Id"] == undefined)}
                                    <button
                                        on:click={() => {
                                            object[property].onclick.apply(
                                                null,
                                                object[property].args,
                                            );
                                            console.log("this gets printed");
                                        }}
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
                                                object[property].args,
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
                            <td
                                >{object[property] === undefined
                                    ? "N/A"
                                    : object[property]}</td
                            >
                        {/if}
                    {/each}
                </tr>
            {/each}
            {/key}
        </table>
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
</style>
