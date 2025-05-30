<script>
   import { onMount } from 'svelte';

   let pointsByCategory = {
      "Total": { max: 10, points: 0 },
      "Professional": { max: 1, points: 0 },
      "Social": { max: 2, points: 0 },
      "Technical": { max: 1, points: 0 },
      "Mentorship": { max: 1, points: 0 },
      "General": { max: 0, points: 0 },
      "Outreach": { max: 2, points: 0 },
   };

   let loading = true;
   let userData = null;

   //Required number of hours for 198 students
   let OUTREACH_REQUIREMENT = 5;


  let userGroups = [];
  let self = false;
  let status = null;
   // Display Own Points and Progress Bar
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
           if (status === null) {
              status = group;
           }
           userGroups.push(group);
        }
     }
     loading = false;
  }

  function getInducteePoints() {
      const categoryMap = {
         general_points: "General",
         mentorship_points: "Mentorship",
         outreach_points: "Outreach",
         professional_points: "Professional",
         social_points: "Social",
         technical_points: "Technical",
         total_points: "Total"
      };

      const userPoints = userData[status] || {};
      Object.entries(categoryMap).forEach(([key, category]) => {
         if (userPoints[key] !== undefined) {
            pointsByCategory[category].points = userPoints[key];
         }
      });

      loading = false;
   }

   // Member and Officer total points
   function getTotalPoints() {
      return leaderboardData?.current_user?.total_points || 0;
   }

   // Member and Officer level calculation
   // Level < 10: n points to level up
   // Level >= 10: 10 points to level up
   function calculateLevel(points) {
       let level = 1, requiredPoints = 1, accumulatedPoints = 0;
       while (points >= accumulatedPoints + requiredPoints) {
           accumulatedPoints += requiredPoints;
           level++;
           requiredPoints = Math.min(level, 10);;
       }
       return { level, progress: points - accumulatedPoints, pointsToNextLevel: requiredPoints };
   }

   let level = 1;
   let progress = 0;
   let pointsToNextLevel = 1;

   // Update level info based on total points
   async function updateLevelInfo() {
      const totalPoints = getTotalPoints();
      const result = calculateLevel(totalPoints);
      level = result.level;
      progress = result.progress;
      pointsToNextLevel = result.pointsToNextLevel;
      console.log(`Total Points: ${totalPoints} | Level ${level} (${progress}/${pointsToNextLevel})`);
   }

   function switchStatus(group) {
      if (status !== group) {
         status = group;
      }
   }

   let leaderboardData = [];
   let isLeaderboardLoading = true;

   // Fetch leaderboard data
   async function getLeaderboardData() {
       try {
           const response = await fetch('/api/leaderboard/');
           if (response.ok) {
               leaderboardData = await response.json();
           } else {
               console.error("Failed to fetch leaderboard data");
           }
       } catch (error) {
           console.error("Error fetching leaderboard data:", error);
       } finally {
           isLeaderboardLoading = false;
       }
   }

   $: if (status && userData) {
   if (status === "Inductee") {
      getInducteePoints();
   } else if (status === "Member" || status === "Officer" || status === "Outreach Student") {
      updateLevelInfo();
   }
   }

   onMount(async() => {
      await getUserData();
      if (userGroups.includes("Inductee")) {
         getInducteePoints();
      }
      if (userGroups.includes("Member") || userGroups.includes("Officer")  || userGroups.includes("Outreach Student")) {
         await getLeaderboardData();
         await updateLevelInfo();
      }
   });
</script>


{#if loading}
   <div class=" mx-5 md:mx-auto max-w-md">
      <div class="bg-white border border-gray-300 rounded-lg shadow-md p-6">
      <div class="animate-pulse space-y-4">
         <div class="h-4 bg-gray-200 rounded w-3/4"></div>
         <div class="h-4 bg-gray-200 rounded w-1/2"></div>
         <div class="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>
      </div>
   </div>
   {:else}
      <div class="mx-5 md:mx-auto hover:shadow-xl transform transition-transform duration-300 ease-in-out">
         <div class="bg-gray-50 active:bg-gray-100 border border-gray-300 rounded-xl shadow-md p-6">
            {#each userGroups as group, i}
               <button class="text-sm text-primary"
               on:click={()=>{switchStatus(group)}}
               >{group}</button>{#if i < userGroups.length - 1}<span class="text-sm text-primary mx-1">|</span>{/if}
            {/each}
            <h2 class="text-lg font-bold text-primary"> {userData.preferred_name} {userData.last_name} </h2>
            <!-- If inductee, show induction points by category -->
            {#if status == "Inductee"}
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
                                 style="width:{category=="General"? Math.min( points * 100, 100) :Math.min((points / max) * 100, 100)}%;"
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
            <!-- If member or officer, show level and progress bar for leaderboard -->
            {:else if status == "Member" || status == "Officer"}
               <div class="border-t border-gray-300 my-3"></div>
               <div class="flex justify-between items-center mb-1">
                  <span class="text-sm font-medium text-primary">Level {level}</span>
                  <span class="text-sm text-primary">
                     {#if leaderboardData?.current_user}
                        {getTotalPoints()}pts
                     {:else}
                        Loading...
                     {/if}
                  </span>
               </div>

               <!-- Progress Bar -->
               <div class="w-full bg-gray-200 rounded-full h-7 flex items-center">
                  <div 
                     class="bg-secondary h-7 rounded-full flex items-center justify-start px-3 text-sm font-medium text-primary" 
                     style="width:{Math.min((progress / pointsToNextLevel) * 100, 100)}%; min-width: 40px;">
                  </div>
                  <div class="flex-1 text-right pr-3 text-sm text-primary">
                     {progress}/{pointsToNextLevel}
                  </div>
               </div>
               <div class="border-t border-gray-300 my-3"></div>

               <!-- Leaderboard Section -->
               {#if !isLeaderboardLoading && leaderboardData.top_users.length > 0}
                  <h3 class="text-lg font-semibold text-primary mb-2">Leaderboard</h3>
                  <div class="space-y-1">
                     {#each leaderboardData.top_users as user, index}
                        <div class="flex items-center justify-between py-1" 
                           class:bg-gray-50={user.user_id === leaderboardData.current_user.user_id}>
                           <div class="flex items-center">
                              <span class="text-primary font-medium mr-2 w-5">{index + 1}.</span>
                              <div class="flex flex-col">
                                 <a href={`/profile/${user.user_id}`} class="text-primary text-sm hover:text-blue-600 transition-colors">
                                    {user.preferred_name} {user.last_name}</a>
                                 <span class="text-xs text-gray-500 -mt-0.5">{user.role}</span>
                              </div>
                           </div>
                           <div class="flex items-center">
                              <span class="text-primary font-medium text-sm">{user.total_points} pts</span>
                           </div>
                        </div>
                        {#if index < leaderboardData.top_users.length - 1}
                           <div class="border-b border-gray-200"></div>
                        {/if}
                     {/each}

                     <!-- Show current user's rank only if not in top 10 -->
                     {#if leaderboardData.current_user && !leaderboardData.top_users.some(user => user.user_id === leaderboardData.current_user.user_id)}
                        <div class="border-b-2 border-gray-300 my-1"></div>
                        <div class="flex items-center justify-between py-1 bg-gray-50">
                           <div class="flex items-center">
                              <span class="text-primary font-medium mr-2 w-5">{leaderboardData.current_user.rank}.</span>
                              <div class="flex flex-col">
                                 <span class="text-primary text-sm">{leaderboardData.current_user.preferred_name} {leaderboardData.current_user.last_name}</span>
                                 <span class="text-xs text-gray-500 -mt-0.5">{leaderboardData.current_user.role}</span>
                              </div>
                           </div>
                           <div class="flex items-center">
                              <span class="text-primary font-medium text-sm">{leaderboardData.current_user.total_points} pts</span>
                           </div>
                        </div>
                     {/if}
                  </div>
               {/if}
            {:else if status === "Outreach Student"}
               <div class="border-t border-gray-300 my-3"></div>
               {#if pointsByCategory["Outreach"]}
                  <div class="space-y-4">
                     <div>
                        <div class="flex justify-between items-center mb-1">
                           <span class="text-sm font-medium text-primary">Outreach</span>
                           <span class="text-sm text-primary">
                              {userData["Outreach Student"].hours ?? 0 }/{OUTREACH_REQUIREMENT} hours
                           </span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-5">
                           <div
                              class="bg-secondary h-5 rounded-full hover:bg-primary hover:scale-105 transition duration-300"
                              style="width:{Math.min(((userData["Outreach Student"].hours  ?? 0) / OUTREACH_REQUIREMENT) * 100 , 100)}%;"
                           ></div>
                        </div>
                     </div>
                  </div>
               {:else}
                  <p class="text-gray-500">No outreach data available.</p>
               {/if}
            {:else}
               <p class="text-gray-500">No points data available.</p>
            {/if}
         </div>
      </div>

{/if}
