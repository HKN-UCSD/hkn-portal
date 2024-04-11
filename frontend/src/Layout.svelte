<!-- Layout.svelte -->
<script>
  import Navbar from "./Components/Navbar.svelte";
  import Sidebar from "./Components/Sidebar.svelte";
  import Feedback from "./Components/Feedback.svelte";
  import { onMount } from "svelte";
  import Device from 'svelte-device-info';

  let isSmallScreen = false;
  if (Device.isPhone || Device.isMobile){
      isSmallScreen = true;    
  }else{
      // Check window size on mount and set the isSmallScreen variable
      onMount(() => {
          isSmallScreen = window.innerWidth <= 769;
      });

      // Add a resize event listener to dynamically update isSmallScreen variable
      window.addEventListener("resize", () => {
          isSmallScreen = window.innerWidth <= 769;
      });
  }
</script>

<main>
  {#if isSmallScreen}
      <div style="display: flex; flex-direction: column;">
        <Navbar/>
        <section style="flex: 1; margin-top: 60px">
          <slot></slot>
        </section>
        <Feedback/>
      </div>
  {:else}
      <div style="display: flex; flex-direction: row;">
        <Sidebar/>
        <section style="flex: 1; margin-left: 254px;">
          <slot></slot>
        </section>
        <Feedback/>
      </div>
  {/if}
</main>

<style>
  /* Styling for the layout */
</style>
