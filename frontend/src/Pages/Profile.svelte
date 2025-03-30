<script>
   import { onMount, onDestroy } from "svelte";
   import Layout from "../Layout.svelte";
   import EventsCard from "../Components/Events/EventsCard.svelte";
   import ProfileInfoEdit from "../Components/ProfileEditInfo.svelte";
   import ProfileIconEdit from "../Components/ProfileEditIcon.svelte";
   import EventPopUp from "../Components/EventPopUp.svelte";
   import { eventGraphics } from "../Components/Events/EventGraphics.js";
   import { fetchUser, userStore } from "../stores.js";

   export let id;
   let editInfo = false;
   let editIcon = false;
   let user = null;
   let userGroups = [];
   let self = false;
   let loading = true;
   let rsvpEvents = [];
   let attendedEvents =[];
   let selectedEvent = null;
   let showPopup = false;
   const curr = new Date().toISOString();

   function handleEventClick(event) {
      console.log(event)
      selectedEvent = event;
      showPopup = true;  
   }

    // Function to close the popup
   function closePopup() {
      showPopup = false;
   }

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
   }

   function getUserGroups() {
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
            pk: event.pk,
            url: `/events/${event.pk}`,
            embed_code: event.embed_code ? event.embed_code : eventGraphics[event.event_type],
            is_draft: event.is_draft,
            points: event.points,
            event_type: event.event_type,
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
            embed_code: event.embed_code ? event.embed_code : eventGraphics[event.event_type],
            points: event.points,
            event_type: event.event_type,
         }
      ));
      attendedEvents = pastEvents;
      attendedEvents.reverse();
   };

   async function updateProfileInfo({ preferred_name, major, grad_year, bio, social_links }) {
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
            degree: user.degree,
            major: major,
            grad_year: grad_year,
            bio: bio,
            social_links: social_links
         }),
      });

      console.log(response);

      if (response.ok) {
         user.preferred_name = preferred_name;
         user.major = major;
         user.grad_year = grad_year;
         user.bio = bio;
         user.social_links = social_links;
         await fetchUser();
      } else {
         console.error("Failed to update profile");
      }
   };

   async function updateProfileIcon({ profile_picture }) {
      let CSRFToken = document.cookie
         .split("; ")
         .find((element) => element.startsWith("csrftoken="))
         .split("=")[1];

      const response = await fetch(`/api/profile/editIcon/`, {
         method: "POST",
         headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": CSRFToken
         },
         body: JSON.stringify({
            profile_picture: profile_picture,
         }),
      });

      console.log(response);

      if (response.ok) {
         user.profile_picture = profile_picture;
         await fetchUser();
      } else {
         console.error("Failed to update profile");
      }
   };

   const onLogOut = (e) => {
        e.preventDefault();
        console.log('Logging out');
        sessionStorage.removeItem('adminStatus');
        sessionStorage.removeItem('interviewEligibility');
        window.location.href = '/accounts/logout/';
    }

   let unsubscribe;

   onMount(async() => {
      if (id) {
         await getUserData();
         getUserGroups();
      } else {
         self = true;
         unsubscribe = userStore.subscribe(value => {
            if (value) {
               user = value;
               getUserGroups();
            }
         })
      }
      await getRSVPs();
      await getCheckOffs();
      const handleKeydown = (event) => {
      if (event.key === "Escape") {
         console.log("Escape Pressed")
         closePopup();
      }
      };
      document.addEventListener("keydown", handleKeydown);
   });

   onDestroy(() => {
      if (unsubscribe) {
         unsubscribe();
      }
   });
</script>

<svelte:head>
    <title> HKN Portal | Profile </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>

<Layout>
   <!-- Overall Container -->
   <h1 class="w-full text-center text-5xl font-bold mt-10 mb-6 p-3 animate-slide-up text-primary transition-transform duration-300 hover:scale-110">Profile</h1>
      
   {#if loading}
      <h2 class="w-full text-center text-3xl font-bold animate-pulse text-primary"> Loading... </h2>
   {:else}
   {#if showPopup}
         <!-- Listens for the dispatch from close on EventPopUp -->
         <EventPopUp event={selectedEvent} on:close={closePopup}  />
   {/if}
   <div class="flex flex-col lg:flex-row gap-6 items-start">
      
      
      <!-- Profile Info -->
      <div class="px-5 lg:px-0 w-full lg:w-1/4">
      <div class="relative bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 w-full lg:max-w-sm border border-gray-300">
         {#if self}
            <button
                  class="absolute top-2 left-2 text-gray-500 hover:text-gray-700 rounded-full p-1.5 hover:bg-gray-200 transition"
                  on:click={(e) => onLogOut(e)}>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
                     <path d="M10 16L6 12m0 0l4-4m-4 4h10m-4-10h6a2 2 0 012 2v16a2 2 0 01-2 2h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
            </button>
            <button
                  class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 rounded-full p-1.5 hover:bg-gray-200 transition"
                  on:click={() => editInfo = true}>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                     <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
            </button>
         {/if}
         <div class="flex flex-col items-center gap-y-4 relative">
            <div class="relative -mt-16">
               <!-- svelte-ignore a11y-click-events-have-key-events -->
               <img src={user.profile_picture}
                     class="w-32 h-32 rounded-full border-4 border-gray-50 shadow-md object-cover bg-white hover:bg-gray-200 hover:border-gray-300 transition"
                     alt="User Avatar"
                     on:click={() => editIcon = true}
                     style="cursor: pointer;">
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
   </div>


      <!-- Events -->
      <div class="space-y-6 w-full lg:w-3/4">
         <!-- Previously Attended Events -->
         <EventsCard title="RSVP'd Events" subtitle="See you there!" events={rsvpEvents} handleEventClick={handleEventClick} />
         <!-- RSVP'd Events -->
         <EventsCard title="Previously Attended Events" subtitle="Thank you for coming!" events={attendedEvents} RSVPEnabled={false} handleEventClick={handleEventClick}/>
      </div>
   </div>

   <!-- Edit Profile Info Modal -->
   <ProfileInfoEdit
      show={editInfo}
      preferred_name={user.preferred_name}
      major={user.major}
      grad_year={user.grad_year}
      bio={user.bio}
      social_links={user.social_links}
      onSave={async ({ preferred_name, major, grad_year, bio, social_links }) => await updateProfileInfo({ preferred_name, major, grad_year, bio, social_links })}
      onClose={() => {editInfo = false}} />

   <!-- Edit Profile Icon Modal -->
   <ProfileIconEdit
      show={editIcon}
      profileIcon={user.profile_picture}
      userGroups={userGroups}
      onSave={async ({ profile_picture }) => await updateProfileIcon({ profile_picture})}
      onClose={() => {editIcon = false}} />
   {/if}
</Layout>