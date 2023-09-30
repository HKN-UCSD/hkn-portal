<script>
   import { onMount } from "svelte";

   let userData = null;

   onMount(async () => {
      try {
         const response = await fetch('/api/profile/');
         if (response.ok) {
            userData = await response.json();
         } else {
            console.error("Failed to fetch user data");
         }
      } catch (error) {
         console.error("Error fetching user data", error);
      }
   });
</script>

<h1>Profile Page</h1>
{#if userData}
   <h2>{userData.first_name} {#if userData.middle_name}{userData.middle_name}{/if} {userData.last_name}</h2>
   {#if userData.inductee_data}
      <h2>{userData.inductee_data.major}</h2>
      <h2>{userData.inductee_data.degree}</h2>
      <h2>{userData.inductee_data.grad_year}</h2>
   {/if}
{/if}