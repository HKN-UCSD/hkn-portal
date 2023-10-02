<script>
    import EventActionButton from "./EventActionButton.svelte";

    export let event;
    async function getEventConsoleTableData() {
        let response = await fetch(`/api/actions/`);
        let availableActions = await response.json();
        let otherActions = availableActions.other_actions;
        return otherActions;
    }

    async function getEventConsoleButtonData() {
        let response = await fetch(`/api/actions/`);
        let availableActions = await response.json();
        let selfActions = availableActions.self_actions;
        return selfActions;
    }
    async function getSelfUser() {
        let response = await fetch(`/api/users/self/`);
        let user = await response.json();
        return user;
    }
    async function getRelevantUserData() {
        let response = await fetch(`/api/events/${event.pk}/relevant_users/`)
        let users = await response.json();
        return users;
    }
</script>
{#await Promise.all([getEventConsoleButtonData(), getSelfUser()])}
    <p>loading...</p>
{:then [selfActions, user]} 
    {#each selfActions as selfAction}
        <EventActionButton event={event} action={selfAction} userActedOn={user}/>
    {/each}
{/await}

{#await Promise.all([getEventConsoleTableData(), getRelevantUserData()])}
<p>loading...</p>
{:then [otherActions, usersData]} 
<table>
{#each usersData as userData}
    <tr>
        <td>
            {userData.first_name} {userData.last_name}
        </td>
        {#each otherActions as otherAction}
        <td>
            <EventActionButton event={event} action={otherAction} userActedOn={userData}/>
        </td>
        {/each}
    </tr>
{/each}
</table>
{/await}

<style>

</style>