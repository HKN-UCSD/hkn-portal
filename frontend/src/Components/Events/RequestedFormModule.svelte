<script>
    export let formURL;
    async function getForm() {
        let response = await fetch(formURL);
        let formhtml = await response.text();
        return formhtml;
    }
</script>

<div>
{#await getForm()}
    <p>Fetching form...</p>
{:then formhtml}
    <p>{formhtml}</p>
    {@html formhtml}
{:catch error}
<p>{error}</p>
{/await}
</div>

<style>
    :global(form) {
        display:grid;
        grid-template-columns: max-content max-content;
        grid-gap:5px;
        vertical-align: middle;
    }
    :global(label) {
        text-align:right; 
    }

    :global(input) {
        display: inline-block;
    }
</style>