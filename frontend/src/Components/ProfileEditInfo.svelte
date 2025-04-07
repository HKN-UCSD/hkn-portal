<script>
    import { onMount, onDestroy } from 'svelte';
    export let show;
    export let preferred_name;
    export let major;
    export let grad_year;
    export let bio;
    export let social_links;
    export let current_courses = [];

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
    let editedCurrentCourses = JSON.parse(JSON.stringify(current_courses));
    let newCourse = { department: '', number: '' };

    // Function to handle adding a new course
    function addCourse() {
      if (!newCourse.department || !newCourse.number) return;
      const department = newCourse.department.trim().toUpperCase();
      const number = newCourse.number.trim().toUpperCase();
      
      if (department.length > 4 || number.length > 4) {
          alert("Invalid department or course number");
          return;
      }
      
      const courseToAdd = { department, number };
      
      // Check for duplicates
      const exists = editedCurrentCourses.some(
          (c) => c.department === department && c.number === number
      );
      
      if (exists) {
          alert("Course already added");
          return;
      }
      
      editedCurrentCourses = [...editedCurrentCourses, courseToAdd];
      newCourse = { department: '', number: '' };
    }
    // Function to handle removing a course
    function removeCourse(course) {
      editedCurrentCourses = editedCurrentCourses.filter((_, index) => index !== course);
    }

    function saveAndClose() {
        onSave({
            preferred_name: editedPreferredName,
            major: editedMajor,
            grad_year: editedGraduationYear,
            bio: editedBio,
            social_links: editedSocialLinks,
            current_courses: editedCurrentCourses
        });
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
  <div class="mt-16 fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" on:click={onCancel}>
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
      <textarea bind:value={editedBio} maxlength="200" class="w-full p-2 border rounded-lg mb-3" placeholder="Introduce yourself!"></textarea>

      <label class="block font-medium mb-2">Current Courses:</label>
      <div class="flex gap-2 mb-2">
        <input 
          type="text" 
          bind:value={newCourse.department} 
          class="w-1/3 p-2 border rounded-lg" 
          placeholder="Dept (e.g. CSE)"
          maxlength="4"
        />
        <input 
          type="text" 
          bind:value={newCourse.number} 
          class="w-2/3 p-2 border rounded-lg" 
          placeholder="Course Number (e.g. 101)"
          maxlength="4"
        />
        <button 
          type="button"
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          on:click={addCourse}
        >
          Add
        </button>
      </div>
      <div class="flex flex-wrap gap-2 mb-3">
        {#each editedCurrentCourses as course, index}
            <div class="flex items-center gap-1 bg-gray-100 px-3 py-1 rounded-lg">
                <span>{course.department} {course.number}</span>
                <button 
                    type="button"
                    class="text-gray-500 hover:text-gray-700"
                    on:click={() => removeCourse(index)}
                >
                    ×
                </button>
            </div>
        {/each}
      </div>

      <label for="instagram-username"class="block font-medium">Instagram Username:</label>
      <input type="url" bind:value={editedSocialLinks.instagram.username} class="w-full p-2 border rounded-lg mb-3"
        placeholder="Your username in Instagram profile" />

      <label for="linkedin-username" class="block font-medium">LinkedIn Username:</label>
      <input type="url" bind:value={editedSocialLinks.linkedin.username} class="w-full p-2 border rounded-lg mb-3" 
        placeholder="Only username after linkedin.com/in/"/>

      <label for="github-username" class="block font-medium">GitHub Username:</label>
      <input type="url" bind:value={editedSocialLinks.github.username} class="w-full p-2 border rounded-lg mb-4"
        placeholder="Your username in GitHub profile"/>

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