<script>
    import { onMount, onDestroy, afterUpdate } from 'svelte';
    export let show;
    export let update;
    export let major;
    export let graduationYear;
    export let bio;
    export let socialLinks;
    export let onSave = () => {};
    export let onClose = () => {};
  
    onMount(() => {
        const handleKeydown = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        }

        document.addEventListener("keydown", handleKeydown);

        onDestroy(() => {
            document.removeEventListener("keydown", handleKeydown);
        });
    });


    let editedMajor = major;
    let editedGraduationYear = graduationYear;
    let editedBio = bio;
    let editedSocialLinks = { ...socialLinks };

    function saveAndClose() {
        onSave({ major: editedMajor, graduationYear: editedGraduationYear, bio: editedBio, socialLinks: editedSocialLinks});
        onClose();
    };

    function onCancel() {
        editedBio = bio;
        editedMajor = major;
        editedGraduationYear = graduationYear;
        editedSocialLinks = { ...socialLinks };
        onClose();
    }

  </script>
  
  {#if show}
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" on:click={onClose}>
      <div class="bg-white p-6 rounded-2xl shadow-lg w-96"
        tabindex=0
        on:click|stopPropagation>
        <h2 class="text-xl font-bold text-center mb-4">Edit Profile</h2>
  
        <label class="block font-medium">Major:</label>
        <input type="text" bind:value={editedMajor} class="w-full p-2 border rounded-lg mb-3" />
  
        <label class="block font-medium">Graduation Year:</label>
        <input type="text" bind:value={editedGraduationYear} class="w-full p-2 border rounded-lg mb-3" />
  
        <label class="block font-medium">Bio (200 characters):</label>
        <textarea bind:value={editedBio} maxlength="200" class="w-full p-2 border rounded-lg mb-3"></textarea>
  
        <label class="block font-medium">Instagram Username:</label>
        <input type="url" bind:value={editedSocialLinks.instagram.username} class="w-full p-2 border rounded-lg mb-3" />
  
        <label class="block font-medium">LinkedIn Username:</label>
        <input type="url" bind:value={editedSocialLinks.linkedin.username} class="w-full p-2 border rounded-lg mb-3" />
  
        <label class="block font-medium">GitHub Username:</label>
        <input type="url" bind:value={editedSocialLinks.github.username} class="w-full p-2 border rounded-lg mb-4" />
  
        <div class="flex justify-between">
          <button 
            class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            on:click={saveAndClose}>
            Save
          </button>
          <button 
            class="bg-gray-300 text-black px-4 py-2 rounded-lg hover:bg-gray-400 transition"
            on:click={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  {/if}