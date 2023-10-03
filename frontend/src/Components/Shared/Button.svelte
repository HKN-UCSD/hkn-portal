<script>
    export let button_text;
    export let on_click;
</script>

<button class="button" on:click={on_click}>{button_text}</button>

<style>
    .button {
        background-color: rgb(0,100,200);
        border: none;
        color: white;
        text-align: center;
        font-size: 16px;
        margin-left: 30px;
    }
</style>