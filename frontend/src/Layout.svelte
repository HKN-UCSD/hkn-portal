<!-- Layout.svelte -->
<script>
  import Navbar from "./Components/Navbar.svelte";
  import { Device, viewport } from './device.js';
  console.log("test")

  const isSmallScreen = derived(viewport, $viewport => $viewport.width <= 769 || Device.isMobile);
</script>

<main>
      <div class="flex min-w-full flex-col">
        <Navbar/>
        <section class="flex-1 container mx-auto">
          <slot></slot>
        </section>
      </div>

</main>

