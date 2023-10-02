<script>
    import RequestedFormModule from "../Components/Events/RequestedFormModule.svelte";

    export let formURL;
</script>
<div>
    <RequestedFormModule {formURL} />
</div>

<style>
    div {
        padding: 30px;
        margin: 30px;
        margin-top: 10px;
    }
</style>