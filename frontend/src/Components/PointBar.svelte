<script>
    import { onMount } from 'svelte';

    let pointsByCategory = {
        "Total": { max: 10},
        "Professional": { max: 1},
        "Social": { max: 2},
        "Technical": { max: 1},
        "Mentorship": {max: 1},
        "General": {max: 0},
        "Outreach": {max: 2},
    };

    Object.keys(pointsByCategory).forEach((category) => {
        pointsByCategory[category].points = 0;
    });

    let loading = true;
    let userData = null;


   let userGroups = [];
   let self = false;
   async function getUserData() {
    try {

        const response = await fetch(`/api/profile/self/`);

        if (response.ok) {
            userData = await response.json();
            self = true;
        } else {
            console.error("Failed to fetch self data");
        }

      } catch (error) {
         console.error("Error fetching user data", error);
      }
      for (let group of ["Inductee", "Member", "Outreach Student", "Officer"]) {

         if (userData[group]) {
            userGroups.push(group);
         }
      }
   }


    async function getEventActionRecords() {
        console.log("fetching event action records");
      return await(await fetch(`/api/eventactionrecords/`)).json();
   }

    async function fetchEventDetails(checkOffs) {
       const events = await Promise.all(
          checkOffs.map(async (record) => {
             const response = await fetch(`/api/events/${record.event}/`);
             const event = await response.json();
             event.earned_points = record.points;
             return event;
          })
       );
       return events;
    }

    async function getCheckOffs() {
       const checkOffs = (await getEventActionRecords()).filter(
          (record) => record.action === "Check Off" && record.acted_on === userData.user_id
       );

       const relevantEvents = await fetchEventDetails(checkOffs);

       const filteredEvents = userGroups.includes("Inductee")
          ? relevantEvents.filter((event) => event.start_time >= userData.induction_class.start_date)
          : relevantEvents.filter((event) => event.earned_points !== 0);

       filteredEvents.forEach((event) => {
          const category = event.event_type || "Unknown"; // Fallback if category is undefined
          pointsByCategory[category].points = (pointsByCategory[category].points || 0) + event.earned_points;
       });
       pointsByCategory["Total"].points = Object.values(pointsByCategory).reduce((acc, { points }) => acc + points, 0);
       loading = false;
    }

    onMount(() => {
        getUserData();
        getCheckOffs();
    });
 </script>

 {#if loading}
    <div class="container mx-auto max-w-md">
        <div class="bg-white border border-gray-300 rounded-lg shadow-md p-6">
        <div class="animate-pulse space-y-4">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
            <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
        </div>
    </div>
 {:else}
 <div class="container mx-auto hover:shadow-xl transform transition-transform duration-300 ease-in-out">
    <div class="bg-white active:bg-gray-100 border border-gray-300 rounded-lg shadow-md p-6">
        <p class="text-sm text-primary">{ userGroups.join(" | ")}</p>
       <h2 class="text-lg font-bold text-primary"> {userData.preferred_name} {userData.last_name} </h2>
       <div class="border-t border-gray-300 my-3"></div>
       {#if Object.keys(pointsByCategory).length}
          <div class="space-y-4">
             {#each Object.entries(pointsByCategory) as [category, {points, max}]}
                <div>
                   <div class="flex justify-between items-center mb-1">
                      <span class="text-sm font-medium text-primary">{category}</span>
                      <span class="text-sm text-primary">{points}/{max} pts</span>
                   </div>
                   <div class="w-full bg-gray-200 rounded-full h-5">
                      <div
                         class="bg-secondary h-5 rounded-full hover:bg-primary hover:scale-105 transition duration-300"
                         style="width:{Math.min((points / max) * 100, 100)}%;"
                      ></div>
                   </div>
                </div>
                {#if category === "Total"}
                   <div class="border-t border-gray-300 my-3"></div>
                {/if}
             {/each}
          </div>
       {:else}
          <p class="text-gray-500">No points data available.</p>
       {/if}
    </div>
 </div>
 {/if}
