<script>
    import { userStore } from '../stores.js';

    let user;
    $: userStore.subscribe(value => {
      if (value) {
        user = value;
      }
    });
  </script>

  <div class="relative inline-block text-left">
    <!-- Profile button -->
      <a href="/profile/self/" class="flex items-center space-x-2" on:click>
      {#if user}
        <img
        class="h-9 w-9 rounded-full object-cover border-2 border-gray-600"
        src="{user.profile_picture}"
        alt="Profile"
      />
      {:else}
        <div
        class="h-9 w-9 rounded-full object-cover border-2 border-gray-600"
      />
      {/if}
      </a>
  </div>
