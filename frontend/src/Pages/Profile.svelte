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

   let rsvpEvents = [];
   let attendedEvents =[];
   const curr = new Date().toISOString();


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
      console.log(futureEvents);
      rsvpEvents = futureEvents;
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
      console.log(pastEvents);
      attendedEvents = pastEvents;
   }

   onMount(async() => {
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
   <div class="flex flex-col lg:flex-row gap-6 items-start">
      <!-- Profile Info -->
      <div class="bg-white p-6 rounded-2xl shadow-lg w-full lg:w-1/3 border rounded-lg hover:shadow-xl transform transition-transform duration-300 ease-in-out ">
         <div class="flex flex-col items-center max-h-[1000px] overflow-x-auto p-3">
               <button class="absolute top-3 right-3 text-primary p-2 hover:text-seconary transition"
                  on:click={() => editProfile = true}>
                  Edit
               </button>
               <img src="/static/MemberProfile.png" class="w-24 h-24 rounded-full bg-secondary" alt="User Avatar">
               <h2 class="mt-4 text-xl font-bold">{user.name}</h2>
               <p class="text-gray-500 p-2">{user.role}</p>
               <p class="text-gray-600 text-sm p-2">{user.major} {user.graduationYear}</p>
               <p class="mt-2 text-sm text-gray-500 h-40 overflow-auto m-2">{user.bio}</p>
               <div class="flex space-x-8 md:space-x-6 mt-4 m-2">
               {#each Object.values(user.socialLinks) as social}
                  <img src="/static/{social.icon}Logo.png" class="h-10 aspect-auto lg:h-12 cursor-pointer p-2" alt="{social.icon} Logo" on:click={() => window.open(social.base_link+social.username)}>
               {/each}
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
</Layout>