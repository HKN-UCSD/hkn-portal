<script>
    import Modal from "./EditPointsModal.svelte";
    import { requestAction, deleteAction } from "./eventutils";

    export let event;
    // The only reason event is added as a parameter is to make the functions rerun
    // when the event changes, thus updating the component.
    // Without this parameter, switching events would let the console stay the same
    // between event switches.
    
    async function getEventConsoleTableData(event) {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.other_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getEventConsoleButtonData(event) {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.self_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
    }
    async function getSelfUser(event) {
        let response = await fetch(`/api/users/self/`);
        if (response.status === 200) {
            let user = await response.json();
            let userRecordResponse = await fetch(`/api/eventactionrecords/pair/${event.pk}/${user.user_id}/`);
            let userRecord = await userRecordResponse.json();
            user["records"] = userRecord;
            return user;
        } else {
            console.log(response.statusText);
            throw new Error(response.statusText);
        }
    }
    async function getRelevantUserData(event) {
        let response = await fetch(`/api/events/${event.pk}/relevant_users/`);
        if (response.status === 200) {
            let users = await response.json();
            let userpromiselist = [];
            // TODO: We should not call API multiple times for similar but specific data. 
            // Such an operation will get slower and slower as more records are added.
            // Add an API endpoint that obtains all of an event's action records
            // that the requesting user is allowed to view. Then, in the 
            // frontend, create a table mapping users to their set of actions. Note that
            // we will have to serialize the user's name and email.
            for (let user of users){
                userpromiselist.push(fetch(`/api/eventactionrecords/pair/${event.pk}/${user.user_id}/`));
            }
            let userdatalistResponses = await Promise.all(userpromiselist);
            let userdatalist = await Promise.all(userdatalistResponses.map((userdataResponse) => userdataResponse.json()))
            for(let i = 0; i < users.length; ++i){
                users[i]["records"] = userdatalist[i]
            }
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }

    let selfActionsPromise = getEventConsoleButtonData(event)

    let modalUserData = false;
</script>
{#await Promise.all([getEventConsoleTableData(event), getRelevantUserData(event), selfActionsPromise, getSelfUser(event)])}
<p>loading...</p>
{:then [otherActions, usersData, selfActions, user]} 

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

{#if otherActions.length > 0}
<h2>Event Console</h2>
<table>
    <tr>
        <th>User</th>
        <th>Email</th>
        {#each selfActions as selfAction}
        <th>
            {selfAction} Time
        </th>
        {/each}
        <th>Points</th>
        {#each otherActions as otherAction}
        <th>
            {otherAction}
        </th>
        {/each}
        <th>
            Edit Points
        </th>
    </tr>
{#each usersData as userData}
<!-- Creates a row consisting of: -->
<!-- Name | Email | RSVP Time | Sign in time | Points | Actions... -->
    <tr>
        <td>
            {userData.preferred_name} {userData.last_name}
        </td>
        <td>
            {userData.email}
        </td>
        {#each selfActions as selfAction}
        <td>
            {#if userData.records.some((record) => record.action == selfAction)}
                {new Date(userData.records.find((record) => record.action == selfAction).action_time).toLocaleString()}
            {/if}
        </td>
        {/each}
        <td>
            {userData.records.some((record) => record.action === "Check Off") ? userData.records.find((record) => record.action === "Check Off").points : 0}
        </td>

        {#each otherActions as otherAction}
        {@const record = userData.records.find((record) => record.action == otherAction)}
        <td>
            {#if record === undefined}
                <button on:click={requestAction(event, otherAction, userData)}>
                    {otherAction}
                </button>
            {:else}
                <button on:click={deleteAction(record.pk)}>
                    un-{otherAction}
                </button>
            {/if}
        </td>

        {/each}

        <td class:faded={!userData.records.some((record) => record.action === "Check Off")}>
            <button on:click={() => {modalUserData = userData}}>Edit Points</button>
        </td>
    </tr>
{/each}
</table>

{/if}
{:catch error}
{alert(error)}
<p>{error}</p>
{/await}

<Modal bind:modalUserData />

<style>
    table, th, td{
        /* border: 1px solid grey; */
        border: none;
        border-collapse: collapse;
    }

    td{
        padding: 10px 15px;
    }

    th {
        padding: 15px;
        /* border-spacing: 5px; */
    }

    th {
        background-color: var(--fc-button-bg-color);
        color: white;
    }

    .faded {
        opacity: 0.5;
    }
    .selfactions {
        display: flex;
        flex-direction: row;
        gap: 10px;
    }
</style>