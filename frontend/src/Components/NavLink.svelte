<script>
    export let text;
    export let link;
</script>

<a href={link} on:click class ="rounded-lg p-2 mx-1 text-sm md:text-lg hover:bg-slate-100 hover:text-primary">
    {text}
</a>