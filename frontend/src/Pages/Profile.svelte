<script>
    import { onMount } from "svelte";
    import Layout from "../Layout.svelte";
    import EventsCard from "../Components/EventsCard.svelte";
    export let id;
    let userData = null;
    let userGroups = [];
    let self = false;
    export let user = {
    name: "Ryan Chen",
    role: "Officer",
    major: "Math-CS 2025",
    bio: "Brief Bio, limit to < 150 words",
    socialLinks: [
      { icon: "instagram", link: "#" },
      { icon: "linkedin", link: "#" },
      { icon: "github", link: "#" }
    ]
  };

  export let attendedEvents = [
    { id: 1, type: "Professional Event", title: "Event 1" },
    { id: 2, type: "Social Event", title: "Event 2" },
    { id: 3, type: "Social Event", title: "Event 3" }
  ];

  export let rsvpEvents = attendedEvents;
 
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
    <!-- Overall Container -->
    <div class="h-100 flex flex-col md:flex-row gap-6 p-6">
        <!-- Profile Info -->
        <div class="bg-white p-6 rounded-2xl shadow-lg w-full md:w-1/4 border rounded-lg hover:shadow-xl transform transition-transform duration-300 ease-in-out">
            <div class="flex flex-col items-center">
                <img src="/static/Avatar.png" class="w-24 h-24 rounded-full" alt="User Avatar">
                <h2 class="mt-4 text-xl font-bold">{user.name}</h2>
                <p class="text-gray-500">{user.role}</p>
                <p class="text-gray-600 text-sm">{user.major}</p>
                <p class="mt-2 text-sm text-gray-500">{user.bio}</p>
                <div class="flex space-x-4 mt-4">
                {#each user.socialLinks as link}
                    <a href={link.link} class="text-secondary hover:text-primary">{link.icon}</a>
                {/each}
                </div>
            </div>
        </div>
      
        <!-- Events -->
        <div class="flex-col space-y-6 ">
            <!-- Previously Attended Events -->
            <div class="bg-white p-6 rounded-2xl shadow-lg border rounded-lg hover:shadow-xl transform transition-transform duration-300 ease-in-out">
                <h3 class="text-lg font-semibold text-primary">Previously Attended Events</h3>
                <p class="text-gray-500">Thank you for coming!</p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <EventsCard />
                </div>
            </div>
      
            <!-- RSVP'd Events -->
            <div class="bg-white p-6 rounded-2xl shadow-lg border rounded-lg hover:shadow-xl transform transition-transform duration-300 ease-in-out">
                <h3 class="text-lg font-semibold text-primary ">RSVP’d Events</h3>
                <p class="text-gray-500">See you there!</p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <EventsCard />
                </div>
            </div>
        </div>
    </div> 
</Layout>