<script>
  import { text } from 'svelte/internal';

import { adminStatus, interviewEligibility } from '../stores.js';
  import NavLink from './NavLink.svelte';
  let logo = "/static/HKN-Logo-New-Blue.png";
  let onLogOut = () => {
      sessionStorage.removeItem('adminStatus');
      sessionStorage.removeItem('interviewEligibility');
  }
let isOpen = true; // Initial state

</script>


<div class="bg-primary text-white">
  <div class="container mx-auto flex h-full my-2 flex-col md:flex-row">
    <div class="flex justify-between items-center">
      <img src={logo} alt="HKN logo" class="h-12 w-12 object-contain mr-4" />
      <!-- Hamburger Menu Icon -->
      <button class="md:hidden text-white focus:outline-none" on:click={() => (isOpen = !isOpen)}>
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
        </svg>
      </button>
    </div>

    <!-- Dropdown Links -->
    <div class={`flex flex-col md:flex-row w-full md:w-auto
      ${isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'}
      transition-all duration-300 overflow-hidden`}>
      <NavLink text='Home' link='/' />
      <NavLink text="Profile" link="/profile/self" />
      {#if $adminStatus === true}
        <NavLink text="Inductees" link="/inductees" />
        <NavLink text="Outreach" link="/outreach" />
      {/if}
      {#if $adminStatus === true || $interviewEligibility === true}
        <NavLink text="Interview Schedule" link="/editschedule" />
      {/if}
      <NavLink text="Logout" link="/accounts/logout/" />
    </div>
  </div>
</div>



<style>
  .transition-all {
    transition: all 0.3s ease;
  }
</style>



