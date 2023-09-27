<script>
    async function getForm() {
        let response = await fetch("/api/events/interface/create/")
        let formhtml = await response.text();
        console.log(formhtml);
        return formhtml;
    }
</script>

{#await getForm()}
    <p>Fetching form...</p>
{:then formhtml} 
    {@html formhtml}
{/await}