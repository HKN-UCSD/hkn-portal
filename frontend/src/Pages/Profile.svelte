<script>
   import { onMount } from "svelte";
   import Layout from "../Layout.svelte";
   import EventsCard from "../Components/Events/EventsCard.svelte";
   import ProfileEdit from "../Components/ProfileEdit.svelte";
   import { embedCode } from "../Components/Events/canvaEmbed";

   export let id;
   let editProfile = false;
   let user = null;
   let userGroups = [];
   let self = false;
   let loading = true;
   let rsvpEvents = [];
   let attendedEvents =[];
   const curr = new Date().toISOString();

   async function getEventActionRecords() {
      return await(await fetch(`/api/eventactionrecords/`)).json();
   }

   async function getUserData() {
      try {
         if (id) {
            const response = await fetch(`/api/profile/${id}/`);
            if (response.ok) {
               user = await response.json();
            } else {
               console.error("Failed to fetch user data");
            }
         } else {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
               user = await response.json();
               id = user.user_id;
               self = true;
            } else {
               console.error("Failed to fetch self data");
            }
         }
      } catch (error) {
         console.error("Error fetching user data", error);
      }

      for (let group of ["Inductee", "Member", "Outreach Student", "Officer"]) {
         if (user[group]) {
            userGroups.push(group);
         }
      }

      console.log(user);
      loading = false;
   };


   /*
    * Fetches RSVP'd events from the server and stores them in rsvpEvents
    */
   async function getRSVPs() {
      let userRSVPs = (await getEventActionRecords()).filter(record => record.action == "RSVP" && record.acted_on == user.user_id);
      let futureEvents = [];
      for (let key of userRSVPs.keys()) {
         let record = userRSVPs[key];
         const event = await(await fetch(`/api/events/${record.event}/`)).json();
         let eventStartTime = new Date(event.start_time);
         if (eventStartTime > Date.now()) {
            futureEvents.push(event);
         }
      }

      futureEvents = futureEvents.filter(event => event.start_time >= curr).map(event => (
         {
            title: event.name,
            description: event.description,
            start_time: event.start_time,
            end_time: event.end_time,
            location: event.location,
            pk: event.pk, url: `/events/${event.pk}`,
            embed_code: event.embed_code ? event.embed_code : embedCode[event.event_type]
         }
      ));
      rsvpEvents = futureEvents;
   };


   /*
    * Fetches checked off events from the server and stores them in attendedEvents
    */
   async function getCheckOffs() {
      const checkOffs = (await getEventActionRecords()).filter(record => record.action == "Check Off" && record.acted_on == user.user_id);
      let pastEvents = [];
      for (let key of checkOffs.keys()) {
         let record = checkOffs[key];
         const event = await(await fetch(`/api/events/${record.event}/`)).json();
         if (record.points != 0) {
            event.earned_points = record.points;
            pastEvents.push(event);
         }
      }

      pastEvents = pastEvents.filter(event => event.start_time < curr).map(event => (
         {
            title: event.name,
            description: event.description,
            start_time: event.start_time,
            end_time: event.end_time,
            location: event.location,
            pk: event.pk, url: `/events/${event.pk}`,
            embed_code: event.embed_code ? event.embed_code : embedCode[event.event_type]
         }
      ));
      attendedEvents = pastEvents;
      attendedEvents.reverse();
   };

   async function updateProfile({ preferred_name,major, grad_year, bio, social_links }) {
      let CSRFToken = document.cookie
        .split("; ")
        .find((element) => element.startsWith("csrftoken="))
        .split("=")[1];

      const response = await fetch(`/api/profile/edit/`, {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRFToken
         },
         body: JSON.stringify({
            preferred_name: preferred_name,
            major: major,
            grad_year: grad_year,
            bio: bio,
            social_links: social_links
         }),
      });
      console.log(response);

      if (response.ok) {
         user.major = major;
         user.grad_year = grad_year;
         user.bio = bio;
         user.social_links = social_links;
      } else {
         console.error("Failed to update profile");
      }

   }


   onMount(async() => {
      await getUserData();
      await getRSVPs();
      await getCheckOffs();
   });
</script>

<svelte:head>
    <title> HKN Portal | Profile </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
   <!-- Overall Container -->
   <h1 class="w-full text-center text-5xl font-bold mt-10 mb-6 animate-slide-up text-primary transition-transform duration-300 hover:scale-110 active:text-secondary">Profile</h1>

   {#if loading}
      <h2 class="w-full text-center text-3xl font-bold animate-pulse text-primary"> Loading... </h2>
   {:else}
   <div class="flex flex-col lg:flex-row gap-6 items-start">
      <!-- Profile Info -->
      <div class="bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 w-full lg:max-w-sm border border-gray-300">
         <div class="flex flex-col items-center gap-y-4 relative">
             {#if self}
                 <button
                     class="absolute top-0 right-0 text-gray-500 hover:text-gray-700 rounded-full p-1.5 hover:bg-gray-200 transition"
                     on:click={() => editProfile = true}>
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                         <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                     </svg>
                 </button>
             {/if}

             <div class="relative -mt-16">
                 <img src="/static/MemberProfile.png"
                      class="w-32 h-32 rounded-full border-4 border-gray-50 shadow-md object-cover bg-white"
                      alt="User Avatar">
             </div>

             <div class="text-center space-y-1">
                 <h2 class="text-2xl font-semibold text-gray-900">{user.preferred_name} {user.last_name}</h2>
                 {#if user.induction_class}
                     <p class="text-sm text-indigo-600 font-medium">{user.induction_class.name}</p>
                 {/if}
             </div>

             <div class="flex flex-wrap justify-center gap-2">
                 {#each userGroups as group, index}
                     <span class="px-3 py-1 bg-gray-200 text-gray-700 rounded-full text-sm font-medium">
                         {group}
                     </span>
                 {/each}
             </div>

             {#if user.major && user.grad_year}
                 <div class="text-center space-y-1">
                     <p class="text-sm text-gray-600">
                         <span class="font-medium">{user.major}</span><br>
                         <span class="text-gray-500">Class of {user.grad_year}</span>
                     </p>
                 </div>
             {/if}

             <div class="w-full pt-4">
                 <div class="bg-white rounded-lg p-4 text-center border border-gray-200">
                     {#if user.bio}
                         <p class="text-gray-600 text-sm leading-relaxed max-h-48 overflow-y-auto">
                             {user.bio}
                         </p>
                     {:else}
                         <p class="text-gray-400 text-sm italic">
                             No bio yet
                         </p>
                     {/if}
                 </div>
             </div>

             <div class="flex gap-4 mt-6">
                 {#each Object.entries(user.social_links) as [platform, data]}
                     {#if data.username}
                         <button
                             class="p-2 rounded-full bg-white hover:bg-gray-100 transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 border border-gray-200"
                             on:click={() => window.open(data.link + data.username)}>
                             <img src={`/static/${platform}Logo.png`}
                                  class="h-6 w-6"
                                  alt="{platform} Logo">
                         </button>
                     {/if}
                 {/each}
             </div>
         </div>
     </div>


      <!-- Events -->
      <div class="space-y-6 w-full lg:w-3/4">
         <!-- Previously Attended Events -->
         <EventsCard title="RSVP'd Events" subtitle="See you there!" events={rsvpEvents} />
         <!-- RSVP'd Events -->
         <EventsCard title="Previously Attended Events" subtitle="Thank you for coming!" events={attendedEvents} RSVPEnabled={false} />
      </div>
   </div>

   <!-- Edit Profile Modal -->
   <ProfileEdit
      show={editProfile}
      preferred_name={user.preferred_name}
      major={user.major}
      grad_year={user.grad_year}
      bio={user.bio}
      social_links={user.social_links}
      onSave={({ preferred_name, major, grad_year, bio, social_links }) => updateProfile({ preferred_name, major, grad_year, bio, social_links })}
      onClose={() => {editProfile = false}} />

   {/if}
</Layout>