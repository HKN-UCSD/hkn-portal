<script>
    import "./eventutils";
    import Modal from "./EditPointsModal.svelte";
    import { userStore } from "../../stores";
    import {
        requestAction,
        deleteAction,
        getAvailableOtherActions,
        getAvailableSelfActions,
    } from "./eventutils";
    import EventRidesDisplay from "./EventRidesDisplay.svelte";
    export let event;
    let eventid = event.pk;

    async function getEventActionButtons(event) {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.self_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
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

        // for each row, add otherAction buttons
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

    let generateTablePromise = generateTable();
    let indexedRows = new Map();

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

    // ACTION BAR SETUP
    generateTablePromise
        .then((rows) => {
            indexedRows = rows;

            // Now that the table is complete, we can see if there's any information
            // about ourself in it. With this information, we can construct the action bar.
            // First we need to know the actions we're allowed to perform on ourselves.
            return getAvailableSelfActions();
        });

    // generate a console table
    let selectedProperties = ["Name", "Check Off", "Points", "Edit Points", "Sign In Time"];
    filters = [(row) => row["Sign In Time"] != undefined];
</script>

<!-- Event Action Bar -->
{#await Promise.all([getEventActionButtons(eventid), getSelfUser(eventid)])}
    <p>Loading...</p>
{:then [selfActions, user]}
    <div class="selfactions">
        {#each selfActions as selfAction}
            {@const record = user.records.find((record) => record.action == selfAction)}
            <!-- If a record was found, provide a delete option; otherwise allow user 
            to take the action -->
            {#if record == undefined}
            <div>
                <button on:click={requestAction(event, selfAction, user)}>
                    {selfAction}
                </button>
            </div>
            {:else}
            <div>
                <button on:click={deleteAction(record.pk)}>
                    un{selfAction}
                </button>
            </div>
            {/if}
        {/each}    
    </div>

    <EventRidesDisplay {event} />

    <h2>Event Console</h2>
    <div class="tab">
        <button
            class="tablinks"
            on:click={() => {
                selectedProperties = ["Name", "Check Off", "Points", "Edit Points", "Sign In Time"];
                filters = [(row) => row["Sign In Time"] != undefined];
            }}>
            Check Off
        </button>
        <button
            class="tablinks"
            on:click={() => {
                selectedProperties = ["Name", "Email", "RSVP Time"];
                filters = [];
            }}>
            RSVP'd
        </button>
    </div>
    {#await generateTablePromise}
        <p>loading...</p>
    {:then tbd}
        <table>
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
                                <button
                                    on:click={object[property].onclick.apply(
                                        null,
                                        object[property].args,
                                    )}>{object[property].text}
                                </button>
                            </td>
                        {:else}
                            <td>{object[property] === undefined ? "N/A" : object[property]}</td>
                        {/if}
                    {/each}
                </tr>
            {/each}
        </table>
    {/await}

    <Modal bind:modalUserData version="1" />
{/await}

<style>
    table,
    th,
    td {
        /* border: 1px solid grey; */
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
</style>
