<script>
  import { onMount, onDestroy } from 'svelte';
  import { getUnlockedIcons } from './ProfileIcons.js';
  import { userStore } from '../stores.js';
  export let show;
  export let profileIcon;
  export let userGroups;
  export let attendedEvents;
  let isHovered = false;

  // User's Level Stuff
  let user = null;
  let leaderboardData = [];
  let level = 0;
  let progress = 0;
  let pointsToNextLevel = 0;
  export let availableProfileIcons = null;

  export let onSave = () => {};
  export let onClose = () => {};

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
      }
  }

  async function updateLevelInfo() {
      const totalPoints = getTotalPoints();
      const result = calculateLevel(totalPoints);
      level = result.level;
      progress = result.progress;
      pointsToNextLevel = result.pointsToNextLevel;
  }

  function getTotalPoints() {
      return leaderboardData?.current_user?.total_points || 0;
  }

  function calculateLevel(points) {
      let level = 1, requiredPoints = 1, accumulatedPoints = 0;
      while (points >= accumulatedPoints + requiredPoints) {
          accumulatedPoints += requiredPoints;
          level++;
          requiredPoints = Math.min(level, 10);;
      }

      return { level, progress: points - accumulatedPoints, pointsToNextLevel: requiredPoints };
  }

  onMount(async () => {
      const handleKeydown = (event) => {
          if (event.key === "Escape") {
              onClose();
          }
      }
      document.addEventListener("keydown", handleKeydown);
      await getLeaderboardData();
      await updateLevelInfo();
      availableProfileIcons = getUnlockedIcons(userGroups, level, attendedEvents);
  });

  let editedProfileIcon = profileIcon;

  function saveAndClose() {
      onSave({ profile_picture: editedProfileIcon });
      onClose();
  };

  function onCancel() {
      editedProfileIcon = profileIcon;
      onClose();
  };

  let tooltipStyle = { left: '0px', top: '0px' };
  function handleMouseMove(event) {
    if (isHovered != null) {
      tooltipStyle = {
          left: `${event.clientX + 75}px`, // offset for better positioning
          top: `${event.clientY - 75}px`, // offset for better positioning
      };
    }
  };

</script>

{#if show}
<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
  class="mt-16 fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" on:click={onCancel}
  on:mousemove={handleMouseMove}>
  <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
  <form class="bg-white p-6 rounded-2xl shadow-lg w-96 lg:w-1/2"
    tabindex=0
    on:click|stopPropagation>

    <!-- svelte-ignore a11y-label-has-associated-control -->
    <label class="block font-medium">Select a Profile Image:</label>
    <div class="grid grid-cols-3 lg:grid-cols-5 gap-4 p-4 max-h-60 overflow-y-auto">
      {#if availableProfileIcons}
        {#each availableProfileIcons as icon}
          {#if icon.unlocked}
            <button
                type="button"
                class="w-30 h-30 border-4 rounded-full p-1 transition-all flex items-center justify-center {editedProfileIcon === icon.path ? 'border-secondary' : 'border-transparent'}"
                on:click={() => editedProfileIcon = icon.path}>
                <img src={icon.path} alt={`${icon.path}`} class="w-20 h-20 rounded-full object-cover aspect-square" />
            </button>
          {:else}
            <div
                class="w-30 h-30 border-4 rounded-full p-1 flex items-center justify-center border-transparent"
                on:mouseenter={() => isHovered = icon.requirements}
                on:mouseleave={() => isHovered = null}>
              <img src={icon.path} alt={`${icon.path}`} class="w-20 h-20 rounded-full object-cover aspect-square opacity-50 bg-gray-200" requirements={icon.requirements}/>
            </div>
            {#if isHovered === icon.requirements}
              <div
                class="absolute p-2 z-30 text-white bg-black bg-opacity-75 rounded-md text-xs"
                style="left: {tooltipStyle.left}; top: {tooltipStyle.top}; transform: translate(-50%, 50%);">
                {icon.requirements}
              </div>
            {/if}
          {/if}
        {/each}
      {/if}
    </div>

    <div class="flex justify-between mt-4">
      <button
        type="submit"
        class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
        on:click={saveAndClose}>
        Save
      </button>
      <button
        type="button"
        class="bg-gray-300 text-black px-4 py-2 rounded-lg hover:bg-gray-400 transition"
        on:click={onCancel}>
        Cancel
      </button>
    </div>
  </form>
</div>
{/if}