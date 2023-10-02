<script>
    export let formURL;
    async function getForm() {
        let response = await fetch(formURL)
        // if (!response.ok) {
        //     return ""
        // }
        let formhtml = await response.text();
        return formhtml;
    }
</script>

<div>
{#await getForm()}
    <p>Fetching form...</p>
{:then formhtml} 
    {@html formhtml}
{:catch error}
<p>{error}</p>
{/await}
</div>