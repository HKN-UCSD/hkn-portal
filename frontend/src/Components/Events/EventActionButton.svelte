<script>
    export let event;
    export let action = "";
    async function requestRSVP(){
        // This isn't exactly how a PUT request should work,
        // but its wasted effort to rewrite the entire attendees
        // list into the put response. We should just be able 
        // to send a request to RSVP with our use data, and 
        // let the backend handle attendee addition.
        const response = await fetch(`/api/events/action/${event.pk}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.cookie.split("; ").find(element => element.startsWith("csrftoken=")).split("=")[1],
            },
            body: JSON.stringify({
                action: action 
            })
        });
        const result = await response.json();
    }
</script>
<button on:click={requestRSVP}>
    <slot />
</button>