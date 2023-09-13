<script>
    export let eventdata;
    // Convert start/end data into a brief, human-readable representation
</script>

<button class="eventlistitem">
    <h4 class="title">{eventdata.name}</h4>
    <p class="category">{eventdata.event_type.name}</p>
    
</button >

<style>
    /* TODO */
    .eventlistitem {
        border-radius: 5px;
        border: none;
        padding: 10px 5% ;
        box-shadow: 0px 1px 2px 1px lightgrey;
        width: 100%;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        overflow: hidden;
    }

    h4 {
    /* h1, h2, h3, h4, h5, h6 { */
        padding: 0px;
        margin: 0px;
    }
    .title, .category{
        margin: 0px 10px;
    }

</style>