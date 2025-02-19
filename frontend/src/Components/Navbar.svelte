<script>
  import { slide } from 'svelte/transition';
  import { adminStatus, interviewEligibility } from '../stores.js';
  import NavLink from './NavLink.svelte';
  import ProfileIcon from './ProfileIcon.svelte';

  let logo = "/static/HKN-Logo-New-Blue.png";
  let isOpen = false; // Mobile menu state

  const onLogOut = (e) => {
    e.preventDefault();
    console.log('Logging out');
    sessionStorage.removeItem('adminStatus');
    sessionStorage.removeItem('interviewEligibility');
    window.location.href = '/accounts/logout/';
  let isOpen = false; // Mobile menu state

  const onLogOut = (e) => {
    e.preventDefault();
    console.log('Logging out');
    sessionStorage.removeItem('adminStatus');
    sessionStorage.removeItem('interviewEligibility');
    window.location.href = '/accounts/logout/';
  }
</script>

<!-- Main Navbar Container -->
<nav class="bg-primary text-white sticky top-0 w-full z-50 shadow">
  <div class="container mx-auto ">
    <div class="flex h-16 justify-between">
      <!-- Logo -->
      <div class="flex items-center">
        <img class="h-10 w-auto object-contain mr-4" src={logo} alt="HKN Logo" />
      </div>

      <!-- Desktop Navigation Links -->
      <div class="hidden md:flex md:items-center md:space-x-6">
        <NavLink text="Home" link="/" />
        {#if $adminStatus === true}
          <NavLink text="Inductees" link="/inductees" />
          <NavLink text="Outreach" link="/outreach" />
        {/if}
        {#if $adminStatus === true || $interviewEligibility === true}
          <NavLink text="Interview Schedule" link="/editschedule" />
        {/if}
        <ProfileIcon />
      </div>

      <!-- Mobile Hamburger Button -->
      <div class="flex items-center md:hidden">
        <button
          class="inline-flex items-center justify-center p-2 rounded-md focus:outline-none"
          on:click={() => isOpen = !isOpen}
          aria-label="Toggle main menu"
        >
          {#if isOpen}
            <!-- Close Icon -->
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12" />
            </svg>
          {:else}
            <!-- Hamburger Icon -->
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          {/if}
        </button>
      </div>
    </div>
  </div>

  {#if isOpen}
    <div class="md:hidden" transition:slide>
      <div class="px-2 pt-2 pb-3 space-y-1 flex flex-col items-center">
        <NavLink text="Home" link="/" />
        {#if $adminStatus === true}
          <NavLink text="Inductees" link="/inductees" />
          <NavLink text="Outreach" link="/outreach" />
        {/if}
        {#if $adminStatus === true || $interviewEligibility === true}
          <NavLink text="Interview Schedule" link="/editschedule" />
        {/if}
        <ProfileIcon />

      </div>
    </div>
  {/if}
</nav>


