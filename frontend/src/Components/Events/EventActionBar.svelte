<script>
    import "./eventutils"
    import { userStore } from "../../stores"
    import { getAvailableSelfActions, requestAction, deleteAction } from "./eventutils";
    import { onDestroy } from "svelte";

    let user = null;
    const unsubscribe = userStore.subscribe((value) => user = value);
    onDestroy(unsubscribe);
</script>
{#await getAvailableSelfActions()}
<p>Loading...</p>
{:then selfActions}
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

{/await}