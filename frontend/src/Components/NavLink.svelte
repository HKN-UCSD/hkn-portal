<script>
    export let text;
    export let link;
</script>

<a
  href={link}
  on:click
  class="relative px-4 py-2 mx-1 text-sm md:text-lg font-medium transition duration-300
         text-white hover:text-white after:block after:h-0.5 after:w-full after:bg-white
         after:scale-x-0 after:transition-transform after:duration-300 hover:after:scale-x-100"
>
  {text}
</a>
