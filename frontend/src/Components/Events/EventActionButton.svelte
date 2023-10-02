<script>
    import { createEventDispatcher } from "svelte";

    export let event;
    export let action;
    export let userActedOn;
    const dispatch = createEventDispatcher();
    async function requestAction(body) {
        console.log(userActedOn)
        const response = await fetch(`/api/eventactionrecords/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.cookie
                    .split("; ")
                    .find((element) => element.startsWith("csrftoken="))
                    .split("=")[1],
            },
            body: JSON.stringify({
                event: event.pk,
                acted_on: userActedOn.user_id,
                action: action,
                extra_data: "{}",
            }),
        });
        const result = await response.json();
        console.log(result);
        dispatch(`eventactioncomplete`, result);
    }

</script>

<button on:click={requestAction}>
    {action}
</button>
