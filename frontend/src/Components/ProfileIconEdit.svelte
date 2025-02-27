<script>
    import { onMount, onDestroy } from 'svelte';
    import { getUnlockedIcons } from './ProfileIcons.js';
    export let show;
    export let profileIcon;
    export let userGroups;

    export let onSave = () => {};
    export let onClose = () => {};
    export let availableProfileIcons = getUnlockedIcons(userGroups);

    onMount(async () => {
        const handleKeydown = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        }
        document.addEventListener("keydown", handleKeydown);
    });

    let editedProfileIcon = profileIcon;

    function saveAndClose() {
        onSave({ profile_picture: editedProfileIcon });
        onClose();
    };

    function onCancel() {
        editedProfileIcon = profileIcon;
        onClose();
    }

</script>

{#if show}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" on:click={onCancel}>
    <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
    <form class="bg-white p-6 rounded-2xl shadow-lg w-96"
      tabindex=0
      on:click|stopPropagation>

      <label class="block font-medium">Select a Profile Image:</label>
      <div class="grid grid-cols-3 gap-4 p-4 max-h-60 overflow-y-auto">
        {#each availableProfileIcons as icon}
          <button
            type="button"
            class="border-4 rounded-full p-1 transition-all {editedProfileIcon === icon.path ? 'border-secondary' : 'border-transparent'}"
            on:click={() => editedProfileIcon = icon.path}
          >
            <img src={icon.path} alt={`${icon.path}`} class="w-20 h-20 rounded-full object-cover" />
          </button>
        {/each}
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