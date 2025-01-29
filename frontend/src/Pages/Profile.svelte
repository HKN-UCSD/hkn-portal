<script>
    import { onMount } from "svelte";
    import Layout from "../Layout.svelte";
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
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
 </svelte:head>
 
 <Layout>
 <main>
    <div style="width: 95%; display: flex; align-items: center; justify-content: space-between;">
       <h1 style="margin-left: 15px">Profile Page</h1>
       {#if self}
          <a id="editProfile" href="/profile/edit/"> Edit </a>
       {/if}
    </div>
    <div class="flex w-full items-center justify-between bg-gray">
        <h1 style="margin-left: 15px">Profile Page</h1>
        {#if self}
            <a id="editProfile" href="/profile/edit/"> Edit </a>
        {/if}
    </div>
    <!-- Overall layout -->
    <div class="flex">
        <!-- Left side profile tab -->
        <div class="w-1/4 bg-secondary">
            <!-- Profile picture -->
             <div class="container mx-auto ovrflow-hidden">
                
               <img class=" w-12 object-contain" src="/static/Avatar.png" alt="Empty Profile Avatar"/>
             </div>
        </div> 
        <!-- Events container -->
        <div class="flex flex-col w-3/4">
            <!-- Previous events -->
            <div>
            </div>
            <!-- RSVP'd events -->
            <div>
            </div>
   </main>
 </Layout>