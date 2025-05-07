<script>
    export let users;
    export let event
</script>

<h3>Notifications Hub</h3>
<form action="/email/event/{event.pk}/" method="post">
    <input type="hidden" name="csrfmiddlewaretoken" value={document.cookie
                    .split("; ")
                    .find((element) => element.startsWith("csrftoken="))
                    .split("=")[1]
    }>
    <label for="recipients">Recipients</label>
    <select id="recipients" multiple required>
        {#each users as user}
            <option value={user.email} selected>{user.email}</option>
        {/each}
    </select>
    <label for="message">Message</label>
    <textarea id="message" rows="4" cols="50"></textarea>
<br/>
    <input type="submit" value="Send" />
</form>

<style>
    /* TODO */
</style>