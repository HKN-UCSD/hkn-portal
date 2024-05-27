<script>
    export let searchText;
</script>

<style>
    .search-bar {
        display: flex;
        padding: 10px;
    }

    input {
        padding: 0.5rem;
        margin-right: 0.5rem;
    }

</style>

<div class="search-bar">
    <input type="text" bind:value={searchText} placeholder="Search..." />
</div>