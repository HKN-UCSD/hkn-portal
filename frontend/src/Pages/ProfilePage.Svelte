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
   {#if userData.inductee_data}
      <h2>{userData.first_name} 
         {#if userData.inductee_data.preferred_name}({userData.inductee_data.preferred_name}) {/if}
         {#if userData.middle_name}{userData.middle_name[0]}. {/if}
         {userData.last_name}
      </h2>
      <h2>Email: </h2><p>{userData.email}</p>
      <h2>Major: </h2><p>{userData.inductee_data.major}</p>
      <h2>Degree: </h2><p>{userData.inductee_data.degree}</p>
      <h2>Graduation Year: </h2><p>{userData.inductee_data.grad_year}</p>
      <div id="induction_points">
         <div>
            <h2>Induction Points</h2>
         </div>
         <div class="points_row">
            <h3>Professional Points: </h3><p>{userData.inductee_data.professional_points} / 2</p>
            <h3>Social Points: </h3><p>{userData.inductee_data.social_points} / 3</p>
            <h3>Technical Points: </h3><p>{userData.inductee_data.technical_points} / 2</p>
         </div>
         <div class="points_row">
            <h3>Outreach Points: </h3><p>{userData.inductee_data.outreach_points} / 2</p>
            <h3>Mentorship Points: </h3><p>{userData.inductee_data.mentorship_points} / 1</p>
            <h3>General Points: </h3><p>{userData.inductee_data.general_points}</p>
            <h3>Total Points: </h3><p>{userData.inductee_data.total_points} / 10</p>
         </div>
      </div>
   {/if}
   {#if userData.member_data}
      <h2>{userData.first_name} 
         {#if userData.member_data.preferred_name}({userData.member_data.preferred_name}) {/if}
         {#if userData.middle_name}{userData.middle_name[0]}. {/if}
         {userData.last_name}
      </h2>
      <h2>Email: </h2><p>{userData.email}</p>
      <h2>Major: </h2><p>{userData.inductee_data.major}</p>
      <h2>Degree: </h2><p>{userData.inductee_data.degree}</p>
      <h2>Graduation Year: </h2><p>{userData.inductee_data.grad_year}</p>
   {/if}
   {#if userData.officer_data}
      <h3>Position: </h3><p>{userData.officer_data.position}</p>
   {/if}
{/if}

<style>
   #induction_points {
      display: flex;
      flex-direction: column;
      height: auto;
      width: auto;
   }

   .points_row {
      display: flex;
      flex-direction: row;
      align-items: center;
   }

</style>