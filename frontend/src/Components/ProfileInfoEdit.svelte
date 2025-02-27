<script>
    import { onMount, onDestroy } from 'svelte';
    export let show;
    export let preferred_name;
    export let major;
    export let grad_year;
    export let bio;
    export let social_links;

    export let onSave = () => {};
    export let onClose = () => {};
    let majors =[];

    const currentYear = new Date().getFullYear();

    // Generate an array of years from the current year to 5 years in the future
    const graduationYears = Array.from({ length: 8 }, (_, i) => currentYear-2 + i);

    onMount(async () => {
        const handleKeydown = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        }
        majors = await (await fetch(`/api/majors/`)).json()
        document.addEventListener("keydown", handleKeydown);
    });

    let editedPreferredName = preferred_name;
    let editedMajor = major;
    let editedGraduationYear = grad_year;
    let editedBio = bio;
    let editedSocialLinks = JSON.parse(JSON.stringify(social_links));

    function saveAndClose() {
        onSave({ preferred_name: editedPreferredName, major: editedMajor, grad_year: editedGraduationYear, bio: editedBio, social_links: editedSocialLinks });
        onClose();
    };

    function onCancel() {
        editedPreferredName = preferred_name;
        editedBio = bio;
        editedMajor = major;
        editedGraduationYear = grad_year;
        editedSocialLinks = JSON.parse(JSON.stringify(social_links));
        onClose();
    }

</script>

{#if show}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div class="mt-16 fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" on:click={onClose}>
    <!-- svelte-ignore a11y-no-noninteractive-tabindex -->
    <form class="bg-white p-6 rounded-2xl shadow-lg w-96 lg:w-1/3"
      tabindex=0
      on:click|stopPropagation>
      <h2 class="text-xl font-bold text-center mb-4">Edit Profile</h2>

      <label for="preferred_name" class="block font-medium" maxlength="65">Preferred Name:</label>
      <input type="text" bind:value={editedPreferredName} class="w-full p-2 border rounded-lg mb-3" />

      <label for="major" class="block font-medium">Major:</label>
      <select bind:value={editedMajor} class="w-full p-2 border rounded-lg mb-3">
          <!-- Add more majors as needed -->
          {#each majors as option}
          <option
              value={option.name} >{option.name}
          </option>
      {/each}
      </select>

      <label for="graduation-year" class="block font-medium">Graduation Year:</label>
      <select bind:value={editedGraduationYear} class="w-full p-2 border rounded-lg mb-3" >
          {#each graduationYears as year}
              <option value={year}>{year} </option>
          {/each}
          <!-- Add more years as needed -->
      </select>

      <label for="bio" class="block font-medium">Bio (200 characters):</label>
      <textarea bind:value={editedBio} maxlength="200" class="w-full p-2 border rounded-lg mb-3"></textarea>

      <label for="instagram-username"class="block font-medium">Instagram Username:</label>
      <input type="url" bind:value={editedSocialLinks.instagram.username} class="w-full p-2 border rounded-lg mb-3" />

      <label for="linkedin-username" class="block font-medium">LinkedIn Username:</label>
      <input type="url" bind:value={editedSocialLinks.linkedin.username} class="w-full p-2 border rounded-lg mb-3" />

      <label for="github-username" class="block font-medium">GitHub Username:</label>
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
    </form>
  </div>
{/if}