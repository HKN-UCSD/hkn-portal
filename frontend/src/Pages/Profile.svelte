<script>
   import { onMount } from "svelte";
 
   export let id;
   let userData = null;
   let userGroups = [];
   let self = false;

   onMount(async () => {
      try {
         if (id) {
            const response = await fetch(`/api/profile/${id}/`);
            if (response.ok) {
               userData = await response.json();
            } else {
               console.error("Failed to fetch user data");
            }
         } else {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
               userData = await response.json();
               id = userData.user_id;
               self = true;
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
      let pastEvents = [];
      if (userGroups.includes("Inductee")) {
         for (let key of checkOffs.keys()) {
            let record = checkOffs[key];
            const event = await(await fetch(`/api/events/${record.event}/`)).json();
            if (event.start_time >= userData.induction_class.start_date) {
               event.earned_points = record.points;
               pastEvents.push(event);
            }
         }
      } else {
         for (let key of checkOffs.keys()) {
            let record = checkOffs[key];
            const event = await(await fetch(`/api/events/${record.event}/`)).json();
            if (record.points != 0) {
               event.earned_points = record.points;
               pastEvents.push(event);
            }
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
    <meta name="viewport" content="width=device-width, initial-sclae=1.0">
</svelte:head>

<main>
   <div style="width: 95%; display: flex; align-items: center; justify-content: space-between;">
      <h1 style="margin-left: 15px">Profile Page</h1>
      <!-- {#if self}
         <a id="editProfile" href="/profile/edit/"> Edit </a>
      {/if} -->
   </div>
      {#if userData}
         <!-- Display basic information -->
         <div class="container" id="basic_info">
            <h2>{userData.first_name} 
               {#if userData.preferred_name != userData.first_name}({userData.preferred_name}) {/if}
               {userData.last_name}
            </h2>
            {#each userGroups as group}
               {#if group == "Inductee" || group == "Member"}
                  <table>
                     <tr>
                        <td><h3>Email:</h3></td>
                        <td><p>{userData.email}</p></td>
                        <td><h3>Major:</h3></td>
                        <td><p>{userData[group].major}</p></td>
                     </tr>
                     <tr>
                        <td><h3>Degree: </h3></td>
                        <td><p>{userData[group].degree}</p></td>
                        <td><h3>Graduation Year: </h3></td>
                        <td><p>{userData[group].grad_year}</p></td>
                     </tr>
                     {#if group == "Member"}
                        <tr>
                           <td><h3>Induction Class:</h3></td>
                           {#if userData.induction_class}
                              <td><p>{userData.induction_class.name}</p></td>
                           {:else}
                              <td><p>None</p></td>
                           {/if}
                        </tr>
                     {/if}
                  </table>
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
                     <table>
                        <tr>
                           <td><h3>Induction Class:</h3></td>
                           <td><p>{userData.induction_class.name}</p></td>
                        </tr>
                        <tr>
                           <td><h3>Professional</h3></td>
                           <td><p>{userData[group].professional_points} / 1</p></td>
                           <td><h3>Social</h3></td>
                           <td><p>{userData[group].social_points} / 2</p></td>
                           <td><h3>Technical</h3></td>
                           <td><p>{userData[group].technical_points} / 1</p></td>
                        </tr>
                        <tr>
                           <td><h3>Outreach</h3></td>
                           <td><p>{userData[group].outreach_points} / 1</p></td>
                           <td><h3>Mentorship</h3></td>
                           <td><p>{userData[group].mentorship_points} / 1</p></td>
                           <td><h3>General</h3></td>
                           <td><p>{userData[group].general_points}</p></td>
                        </tr>
                        <tr>
                           <td><h3>Total</h3></td>
                           <td><p>{userData[group].total_points} / 10</p></td>
                        </tr>
                     </table>

                  <!-- Display outreach student information -->
                  {:else if group == "Outreach Student"}
                     <table>
                        <tr>
                           <td><h3>Outreach course:</h3></td>
                           <td><p>{userData[group].outreach_course}</p></td>
                           <td><h3>Quarter:</h3></td>
                           <td><p>{userData[group].quarter}</p></td>
                           <td><h3>Hours:</h3></td>
                           <td><p>{userData[group].hours}</p></td>
                           <td><h3>Car:</h3></td>
                           <td><p>{userData[group].car}</p></td>
                        </tr>
                     </table>

                  <!-- Display officer information -->
                  {:else if group == "Officer"}
                     <table>
                        <tr>
                           <td><h3>Position:</h3></td>
                           <td><p>{userData[group].position}</p></td>
                        </tr>
                        <!-- Add house information once house system is implemented-->
                     </table>
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
   #editProfile{
      color: white;
      margin-left: 15px;
      margin-bottom: 20px;
      border-radius: 0.25em;
      padding: 0.4em 0.65em;
      background-color: var(--fc-button-bg-color);
      border: none;
      outline: none;
   }
   .container {
      padding: 10px 10px;
      border-radius: 5px;
      box-shadow: 0px 1px 2px 1px lightgray;
      grid-area: c;
      margin: 10px;
      background-color: #f5f5f5;
      width: 95%;
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

   tr {
      max-width: 100%;
      width: 50%;
   }

   th, td {
      padding: 5px 20px 5px 0px;
   }

   table {
      max-width: 100%;
      width: 100%;
      text-align: left;
      table-layout: fixed;
   }

   @media screen and (max-width: 600px) {
      #basic_info {
         display: block;
      }
      #basic_info tr > td {
         width: 40%;
         display: inline-block
      }
   }
</style>