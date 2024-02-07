<script>
   import { onMount } from "svelte";
 
   export let id;
   let userData = null;

   onMount(async () => {
      try {
         if (id) {
            let response = await fetch(`/api/profile/${id}/`);
            if (response.ok) {
               userData = await response.json();
            } else {
               console.error("Failed to fetch user data");
            }
         }
         if (!userData) {
            let response = await fetch('/api/profile/');
            if (response.ok) {
               userData = await response.json();
            } else {
               console.error("Failed to fetch self data");
            }
         }
      } catch (error) {
         console.error("Error fetching user data", error);
      }
   });
</script>

<svelte:head>
    <title> HKN Portal | Profile </title>
</svelte:head>

<main>
   <h1 style="margin-left: 15px">Profile Page</h1> <!--TODO: Use permissions groups api to get list of groups and create a card for each group instead of doing combinations-->    
      {#if userData}
         {#if userData.inductee_data}
            <div class="container">
               <h2>{userData.first_name} 
                  {#if userData.preferred_name != userData.first_name}({userData.preferred_name}) {/if}
                  {#if userData.middle_name}{userData.middle_name[0]}. {/if}
                  {userData.last_name}
               </h2>
               <div class="multi-row">
                  <div class="multi-column">
                     {#if userData.outreach_data}
                        <p>Inductee, Outreach Student</p>
                     {:else}
                        <p>Inductee</p>
                     {/if}
                  </div>
                  <div class="multi-column">
                     <h3>Email: </h3><p>{userData.email}</p>
                     <h3>Major: </h3><p>{userData.inductee_data.major}</p>
                  </div>
                  <div class="multi-column">
                     <h3>Degree: </h3><p>{userData.inductee_data.degree}</p>
                     <h3>Graduation Year: </h3><p>{userData.inductee_data.grad_year}</p>
                  </div>
               </div>
            </div>
            <div class="container">
               <div class="multi-row" id="profile">
                  <div>
                     <h3>Induction Points</h3>
                  </div>
                  <div class="multi-column">
                     <h3>Professional </h3><p>{userData.inductee_data.professional_points} / 1</p>
                     <h3>Social </h3><p>{userData.inductee_data.social_points} / 2</p>
                     <h3>Technical </h3><p>{userData.inductee_data.technical_points} / 1</p>
                  </div>
                  <div class="multi-column">
                     <h3>Outreach </h3><p>{userData.inductee_data.outreach_points} / 1</p>
                     <h3>Mentorship </h3><p>{userData.inductee_data.mentorship_points} / 1</p>
                     <h3>General </h3><p>{userData.inductee_data.general_points}</p>
                     <h3>Total </h3><p>{userData.inductee_data.total_points} / 10</p>
                  </div>
               </div>
            </div>
         {:else if userData.member_data}
            <div class="container">
               <h2>{userData.first_name} 
                  {#if userData.preferred_name != userData.first_name}({userData.preferred_name}) {/if}
                  {#if userData.middle_name}{userData.middle_name[0]}. {/if}
                  {userData.last_name}
               </h2>
               <div class="multi-row">
                  <div class="multi-column">
                     {#if userData.officer_data && userData.outreach_data}
                        <p>Officer ({userData.officer_data.position}), Outreach Student</p>
                     {:else if userData.officer_data}
                        <p>Officer ({userData.officer_data.position})</p>
                     {:else if userData.outreach_data}
                        <p>Member, Outreach Student</p>
                     {:else}
                        <p>Member</p>
                     {/if}
                  </div>
                  <div class="multi-column">
                     <h3>Email: </h3><p>{userData.email}</p>
                     <h3>Major: </h3><p>{userData.member_data.major}</p>
                  </div>
                  <div class="multi-column">
                     <h3>Degree: </h3><p>{userData.member_data.degree}</p>
                     <h3>Graduation Year: </h3><p>{userData.member_data.grad_year}</p>
                  </div>
               </div>
            </div>
         {:else}
            <div class="container">
               <h2>{userData.first_name} {userData.last_name}</h2>
               <div class="multi-row">
                  <div class="multi-column">
                     <p>Guest</p>
                  </div>
                  <div class="multi-column">
                     <h3>Email: </h3><p>{userData.email}</p>
                  </div>
               </div>
            </div>
         {/if}
         {#if userData.outreach_data}
            <div class="container">
               <div>
                  <h2>Outreach Information</h2>
               </div>
               <div class="multi-row">
                  <div class="multi-column">
                     <h3>Outreach course: </h3><p>{userData.outreach_data.outreach_course}</p>
                     <h3>Hours: </h3><p>{userData.outreach_data.hours}</p>
                     <h3>Car: </h3><p>{userData.outreach_data.car}</p>
                  </div>
               </div>
            </div>
         {/if}
      {/if}
</main>

<style>
   .container {
      padding: 10px 10px;
      border-radius: 5px;
      box-shadow: 0px 1px 2px 1px lightgray;
      grid-area: c;
      margin: 10px;
      background-color: #f5f5f5;
   }

   .multi-row {
      display: flex;
      flex-direction: column;
      height: auto;
      width: 100%;
      margin: 10px 0px 10px 0px;
   }

   .multi-column {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin: 10px 0px 10px 0px;
   }

   h2 {
      margin: 0px 10px 0px 0px;
      
   }

   h3 {
      margin: 0px 10px 0px 0px;
      min-width: 20px;
   }

   p {
      margin: 0px 25px 0px 0px;
   }

</style>