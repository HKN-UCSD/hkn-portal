<script>
   import { onMount } from "svelte";
   import Layout from "../Layout.svelte";
   import EventsCard from "../Components/Events/EventsCard.svelte";
   import ProfileEdit from "../Components/ProfileEdit.svelte";
   import { embedCode } from "../Components/Events/canvaEmbed";

    export let id;

    let editProfile = false;
    let update = true;
    let userData = null;
    let userGroups = [];
    let self = false;
    export let user = {
    name: "Ryan Chen",
    role: "Officer",
    major: "Math-CS",
    graduationYear: 2025,
    bio: "Ryan Chen is a Mathematics-Computer Science student at UC San Diego, graduating in June 2025. Passionate about software engineering, he enjoys solving complex problems with efficient algorithms and scalable systems. His interests include AI, distributed computing, and full-stack development. \n As an HKN officer, Ryan fosters a strong community through mentorship, technical workshops, and networking events, upholding HKN’s core pillars: Scholarship, Attitude, and Character. He has experience with large-scale cloud infrastructure and optimizing machine learning models. Proficient in Python, JavaScript, and C++, he works with frameworks like React, Node.js, and TensorFlow. Another sentence with more words to make word count 100.",
    socialLinks: {
      instagram: { icon: "Instagram", base_link: "https://www.instagram.com/", username: "ryanyychen" },
      linkedin: { icon: "LinkedIn", base_link: "https://www.linkedin.com/in/", username: "yu-you-ryan-chen" },
      github: { icon: "GitHub", base_link: "https://www.github.com/", username: "ryanyychen" }
    }
   };

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
      <div class="bg-white p-6 rounded-2xl shadow-lg w-full lg:w-1/3 border rounded-lg hover:shadow-xl transform transition-transform duration-300 ease-in-out ">
         <div class="flex flex-col items-center max-h-[1000px] overflow-x-auto p-3">
               <button class="absolute top-3 right-3 text-primary p-2 hover:text-seconary transition"
                  on:click={() => editProfile = true}>
                  Edit
               </button>
               <img src="/static/MemberProfile.png" class="w-24 h-24 rounded-full bg-secondary" alt="User Avatar">
               <h2 class="mt-4 text-xl font-bold">{user.preferred_name} {user.last_name}</h2>
               <p class="text-gray-500 pt-2 pr-2 pl-2">
                  {#each userGroups as group, index}
                     {#if index > 0}{" | "}{/if}
                     {group}
                  {/each}
               </p>
               {#if user.induction_class}
                  <p class="text-gray-600 text-sm pb-2">{user.induction_class.name}</p>
               {/if}
               {#if user.major && user.grad_year}
                  <p class="text-gray-600 text-sm p-2">{user.major} {user.grad_year}</p>
               {/if}
               {#if user.bio}
                  <p class="mt-2 text-sm text-gray-500 h-40 overflow-auto m-2">{user.bio}</p>
               {:else}
                  <p class="mt-2 text-sm text-gray-500 h-40 overflow-auto m-2">This user hasn't input a bio yet.</p>
               {/if}
               <div class="flex space-x-8 md:space-x-6 mt-4 m-2">
               <img src="/static/InstagramLogo.png" class="h-10 aspect-auto lg:h-12 cursor-pointer p-2" alt="Instagram Logo" on:click={() => window.open(user.social_links.instagram.link+user.social_links.instagram.username)}>
               <img src="/static/LinkedInLogo.png" class="h-10 aspect-auto lg:h-12 cursor-pointer p-2" alt="LinkedIn Logo" on:click={() => window.open(user.social_links.linkedin.link+user.social_links.linkedin.username)}>
               <img src="/static/GitHubLogo.png" class="h-10 aspect-auto lg:h-12 cursor-pointer p-2" alt="GitHub Logo" on:click={() => window.open(user.social_links.github.link+user.social_links.github.username)}>
               </div>
         </div>
      </div>


      <!-- Events -->
      <div class="space-y-6 w-full lg:w-2/3">
         <!-- Previously Attended Events -->
         <EventsCard title="RSVP'd Events" subtitle="See you there!" events={rsvpEvents} />
         <!-- RSVP'd Events -->
         <EventsCard title="Previously Attended Events" subtitle="Thank you for coming!" events={attendedEvents} RSVPEnabled={false} />
      </div>
   </div>

   <!-- Edit Profile Modal -->
   <ProfileEdit
      show={editProfile}
      major={user.major}
      grad_year={user.grad_year}
      bio={user.bio}
      social_links={user.social_links}
      onSave={({ major, grad_year, bio, social_links }) => {
         user.major = major;
         user.grad_year = grad_year;
         user.bio = bio;
         user.social_links = social_links;
         editProfile = false;
      }}
      onClose={() => {editProfile = false}} />

   {/if}
</Layout>