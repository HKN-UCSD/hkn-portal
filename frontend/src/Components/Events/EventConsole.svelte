<script>
    import EventActionButton from "./EventActionButton.svelte";

    export let event;
    // The only reason event is added as a parameter is to make the functions rerun
    // when the event changes, thus updating the component.
    // Without this parameter, switching events would let the console stay the same
    // between event switches.
    
    async function getEventConsoleTableData(event) {
        let response = await fetch(`/api/actions/`);
        let availableActions = await response.json();
        let otherActions = availableActions.other_actions;
        return otherActions;
    }

    async function getEventConsoleButtonData(event) {
        let response = await fetch(`/api/actions/`);
        let availableActions = await response.json();
        let selfActions = availableActions.self_actions;
        return selfActions;
    }
    async function getSelfUser(event) {
        let response = await fetch(`/api/users/self/`);
        let user = await response.json();
        let userRecordResponse = await fetch(`/api/eventactionrecords/pair/${event.pk}/${user.user_id}/`);
        let userRecord = await userRecordResponse.json();
        user["records"] = userRecord;
        return user;
    }
    async function getRelevantUserData(event) {
        let response = await fetch(`/api/events/${event.pk}/relevant_users/`)
        let users = await response.json();
        let userpromiselist = [];
        for (let user of users){
            userpromiselist.push(fetch(`/api/eventactionrecords/pair/${event.pk}/${user.user_id}/`));
        }
        let userdatalistResponses = await Promise.all(userpromiselist);
        let userdatalist = await Promise.all(userdatalistResponses.map((userdataResponse) => userdataResponse.json()))
        for(let i = 0; i < users.length; ++i){
            users[i]["records"] = userdatalist[i]
        }
        return users;
    }

    let selfActionsPromise = getEventConsoleButtonData(event)
</script>

{#await Promise.all([getEventConsoleTableData(event), getRelevantUserData(event), selfActionsPromise, getSelfUser(event)])}
<p>loading...</p>
{:then [otherActions, usersData, selfActions, user]} 
{#each selfActions as selfAction}
    <div class:faded={user.records.some((record) => record.action == selfAction)}>
        <EventActionButton event={event} action={selfAction} userActedOn={user}/>
    </div>
{/each}
<table>
    <tr>
        <th>User</th>
        {#each selfActions as selfAction}
        <th>
            {selfAction} Time
        </th>
        {/each}
        {#each otherActions as otherAction}
        <th>
            {otherAction}
        </th>
        {/each}
    </tr>
{#each usersData as userData}
    <tr>
        <td>
            {userData.first_name} {userData.last_name}
        </td>
        {#each selfActions as selfAction}
        <td>
            {#if userData.records.some((record) => record.action == selfAction)}
                {new Date(userData.records.find((record) => record.action == selfAction).action_time).toLocaleString()}
            {/if}
        </td>
        {/each}
        {#each otherActions as otherAction}
        <td class:faded={userData.records.some((record) => record.action == otherAction)}>
            <EventActionButton event={event} action={otherAction} userActedOn={userData}/>
        </td>
        {/each}
    </tr>
{/each}
</table>
{/await}

<style>
    table, th, td{
        border: 1px solid grey;
    }

    .faded {
        opacity: 0.5;
    }
</style>