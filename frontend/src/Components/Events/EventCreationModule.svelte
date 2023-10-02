<script>
    async function getForm() {
        let response = await fetch("/api/interface/create/")
        let formhtml = await response.text();
        return formhtml;
    }
</script>

{#await getForm()}
    <p>Fetching form...</p>
{:then formhtml} 
    {@html formhtml}
{/await}