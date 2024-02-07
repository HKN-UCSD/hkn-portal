<script>
   import { onMount } from "svelte";
 
   export let id;
   let userData = null;
   let userGroups = [];

   onMount(async () => {
      try {
         if (id) {
            const response = await fetch(`/api/profile/${id}/`);
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
      for (let group of ["Inductee", "Member", "Outreach Student", "Officer"]) {
         if (userData[group]) {
            userGroups.push(group);
         }
      }
   });

   async function getEventActionRecords() {
      return await(await fetch(`/api/eventactionrecords/`)).json();
   }

   async function getRSVPs() {
      let userRSVPs = (await getEventActionRecords()).filter(record => record.action == "RSVP" && record.acted_on == userData.user_id);
      let futureEvents = [];
      for (let key of userRSVPs.keys()) {
         let record = userRSVPs[key];
         const event = await(await fetch(`/api/events/${record.event}/`)).json();
         let eventStartTime = new Date(event.start_time);
         if (eventStartTime > Date.now()) {
            futureEvents.push(event);
         }
      }

      futureEvents.sort((a,b) => 
         (new Date(a.start_time)) - (new Date(b.start_time))
      );

      for (let event of futureEvents) {
         let eventStartTime = new Date(event.start_time)
         event.start_time = eventStartTime.toLocaleString(undefined, {
            timeszone: 'UTC',
            dateStyle: 'long',
            timeStyle: 'short',
         });
      }

      return futureEvents;
   }

   async function getCheckOffs() {
      const checkOffs = (await getEventActionRecords()).filter(record => record.action == "Check Off" && record.acted_on == userData.user_id);
      console.log(checkOffs);
      let pastEvents = [];
      for (let key of checkOffs.keys()) {
         let record = checkOffs[key];
         const event = await(await fetch(`/api/events/${record.event}/`)).json();
         console.log(record);
         if (record.points != 0) {
            event.earned_points = record.points;
            pastEvents.push(event);
         }
      }

      pastEvents.sort((a,b) => 
         (new Date(b.start_time)) - (new Date(a.start_time))
      );

      for (let event of pastEvents) {
         let eventStartTime = new Date(event.start_time)
         event.date = eventStartTime.toLocaleString(undefined, {
            timeszone: 'UTC',
            dateStyle: 'long',
         });
      }

      return pastEvents;
   }
</script>

<svelte:head>
    <title> HKN Portal | Profile </title>
</svelte:head>

<main>
   <h1 style="margin-left: 15px">Profile Page</h1> <!--TODO: Use permissions groups api to get list of groups and create a card for each group instead of doing combinations-->    
      {#if userData}
         <!-- Display basic information -->
         <div class="container" id="basic_info">
            <h2>{userData.first_name} 
               {#if userData.preferred_name != userData.first_name}({userData.preferred_name}) {/if}
               {#if userData.middle_name}{userData.middle_name[0]}. {/if}
               {userData.last_name}
            </h2>
            {#each userGroups as group}
               {#if group == "Inductee" || group == "Member"}
                  <div class="multi-row">
                     <div class="multi-column">
                        <h3>Email: </h3><p>{userData.email}</p>
                        <h3>Major: </h3><p>{userData[group].major}</p>
                     </div>
                     <div class="multi-column">
                        <h3>Degree: </h3><p>{userData[group].degree}</p>
                        <h3>Graduation Year: </h3><p>{userData[group].grad_year}</p>
                     </div>
                     {#if group == "Member"}
                        <div class="multi-column">
                           <h3>Induction Class: </h3><p>{userData.induction_class}</p>
                        </div>
                     {/if}
                  </div>
               {/if}
            {/each}
         </div>

         <!-- Display cards for each group -->
         {#each userGroups as group}
            {#if group != "Member"}
               <div class="container">
                  <h2>{group}</h2>
                  <!-- Display induction information -->
                  {#if group == "Inductee"}
                     <div class="multi-row">
                        <div class="multi-column">
                           <h3>Induction Class: </h3><p>{userData.induction_class}</p>
                        </div>
                        <div class="multi-column">
                           <h3>Professional </h3><p>{userData[group].professional_points} / 1</p>
                           <h3>Social </h3><p>{userData[group].social_points} / 2</p>
                           <h3>Technical </h3><p>{userData[group].technical_points} / 1</p>
                        </div>
                        <div class="multi-column">
                           <h3>Outreach </h3><p>{userData[group].outreach_points} / 1</p>
                           <h3>Mentorship </h3><p>{userData[group].mentorship_points} / 1</p>
                           <h3>General </h3><p>{userData[group].general_points}</p>
                           <h3>Total </h3><p>{userData[group].total_points} / 10</p>
                        </div>
                     </div>

                  <!-- Display outreach student information -->
                  {:else if group == "Outreach Student"}
                     <div class="multi-row">
                        <div class="multi-column">
                           <h3>Outreach course: </h3><p>{userData[group].outreach_course}</p>
                           <h3>Hours: </h3><p>{userData[group].hours}</p>
                           <h3>Car: </h3><p>{userData[group].car}</p>
                        </div>
                     </div>
                  
                  <!-- Display officer information -->
                  {:else if group == "Officer"}
                     <div class="multi-row">
                        <div class="multi-column">
                           <h3>Position: </h3><p>{userData[group].position}</p>
                           <!-- Add house information once house system is implemented-->
                        </div>
                     </div>
                  {/if}
               </div>
            {/if}
         {/each}

         <!-- Display event attendence information -->
         {#await getRSVPs()}
            <p>Loading...</p>
         {:then futureEvents}
            <div class="container">
               <h2>RSVP'd Events</h2>
               {#if futureEvents.length != 0}
                  <table>
                     <tr>
                        <th> Name </th>
                        <th> Start Time </th>
                        <th> Location </th>
                        <th> Type </th>
                     </tr>
                     {#each futureEvents as event}
                        <tr>
                           <td><a href="/events/{event.pk}/">{event.name}</a></td>
                           <td>{event.start_time}</td>
                           <td>{event.location}</td>
                           <td>{event.event_type}</td>
                        </tr>
                     {/each}
                  </table>
               {:else}
                  <p> No RSVP'd Events</p>
               {/if}
            </div>
         {/await}

         <!-- {#each userGroups as group}
            {#if group == "Inductee"} -->
               {#await getCheckOffs()}
                  <p>Loading...</p>
               {:then checkOffs}
                  <div class="container">
                     <h2>Checked Off Events</h2>
                     {#if checkOffs.length != 0}
                        <table>
                           <tr>
                              <th> Name </th>
                              <th> Points Earned </th>
                              <th> Type </th>
                              <th> Date </th>
                           </tr>
                           {#each checkOffs as event}
                              <tr>
                                 <td><a href="/events/{event.pk}/">{event.name}</a></td>
                                 <td>{event.earned_points}</td>
                                 <td>{event.event_type}</td>
                                 <td>{event.date}</td>
                              </tr>
                           {/each}
                        </table>
                     {:else}
                        <p> No checked off events </p>
                     {/if}
                  </div>
               {/await}
            <!-- {/if}
         {/each} -->
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

   table {
      text-align: left;
   }

   th, td {
      padding: 5px 20px 5px 0px;
   }
</style>