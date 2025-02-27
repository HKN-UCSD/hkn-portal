<script>
    import { onMount } from 'svelte';
    import { slide } from 'svelte/transition';
    import { userStore } from '../stores.js';

    let user;
    $: userStore.subscribe(value => {
      if (value) {
        user = value;
      }
    });
    let open = false;
    let dropdownRef;

    // Toggle the dropdown
    function toggle() {
      open = !open;
    }

    const onLogOut = (e) => {
        e.preventDefault();
        console.log('Logging out');
        sessionStorage.removeItem('adminStatus');
        sessionStorage.removeItem('interviewEligibility');
        window.location.href = '/accounts/logout/';
    }


    // Close the dropdown when clicking outside
    function handleClickOutside(event) {
      if (dropdownRef && !dropdownRef.contains(event.target)) {
        open = false;
      }
    }

    onMount(async() => {
      document.addEventListener('click', handleClickOutside, true);
      return () =>
        document.removeEventListener('click', handleClickOutside, true);
    });
  </script>

  <div class="relative inline-block text-left" bind:this={dropdownRef}>
    <!-- Profile button -->
    <button
      on:click={toggle}
      class="flex items-center focus:outline-none"
      aria-haspopup="true"
      aria-expanded={open}
    >
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
      <!-- Dropdown arrow icon -->
      <svg
        class="ml-2 h-5 w-5 text-gray-600"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.23 8.29a.75.75 0 01.02-1.08z"
          clip-rule="evenodd"
        />
      </svg>
    </button>

    <!-- Dropdown menu -->
    {#if open}
      <div
        transition:slide
        class="origin-top-right absolute right-0 mt-2 w-40 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10"
      >
        <div class="py-1">
          <a
            href="/profile/self/"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >Profile</a
          >
          <a
            href="/accounts/logout/"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            on:click={(e) => {
                onLogOut(e);
            }}
            >Logout</a
          >
        </div>
      </div>
    {/if}
  </div>
