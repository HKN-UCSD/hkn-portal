<script>
  import { text } from 'svelte/internal';
import { adminStatus, interviewEligibility } from '../stores.js';
  import NavLink from './NavLink.svelte';
  let logo = "/static/HKN-Logo-New-Blue.png";
  let onLogOut = () => {
      sessionStorage.removeItem('adminStatus');
      sessionStorage.removeItem('interviewEligibility');
  }
</script>



  <div class="bg-primary text-white">
    <div class="container mx-auto flex h-full my-2 ">
    <img src={logo} alt="HKN logo" class=" h-12 w-12 object-contain mr-4" />
    <NavLink  text='Home' link='/'/>
    <NavLink text="Profile" link="/profile/self"/>
    {#if $adminStatus === true}
      <NavLink text="Inductees" link="/inductees"/>
      <NavLink text="Outreach" link="/outreach"/>
    {/if}
    {#if $adminStatus === true || $interviewEligibility === true}
      <NavLink text="Interview Schedule" link="/editschedule"/>
    {/if}



    <a href="/accounts/logout/" on:click={onLogOut}>Logout</a>

  </div>
</div>