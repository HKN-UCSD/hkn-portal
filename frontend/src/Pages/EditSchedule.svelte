<script>
  import { onMount } from "svelte";
  import Layout from "../Layout.svelte";
  export let id;
  let userData = null;
  let userGroups = [];
  let self = false;
  let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  let availabilityMatrix = Array.from({ length: 11 }, () => Array(7).fill(0));
  let timeSlots = Array.from({ length: 8 }, (_, i) => 10 + i); // 7 AM to 5 PM

  onMount(async () => {
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
  });

    // 2D array for availability (all set to 0 initially)
    
    // Toggle availability on cell click
  async function toggleAvailability(row, col) {
    availabilityMatrix[row][col] = 1 - availabilityMatrix[row][col]; // Toggle between 1 and 0
  }

  
  //CHECK OFFICER VS INDUCTEE AND CALL API 
  async function submitAvailability() {
        try {
            const response = await fetch(`/api/officers/${OfficerId}/update-availability/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}` // Include auth token if required
                },
                body: JSON.stringify({ availability: availabilityMatrix }),
            });

            if (response.ok) {
                const data = await response.json();
                alert('Availability submitted successfully!');
                console.log('Response from backend:', data);
            } else {
                const errorData = await response.json();
                alert('Failed to submit availability: ' + errorData.error);
                console.error('Error:', errorData);
            }
        } catch (error) {
            alert('An error occurred while submitting availability.');
            console.error('Error:', error);
        }
    }
</script>

<style>
  table {
      border-collapse: collapse;
      width: 100%;
  }
  th, td {
      border: 1px solid #ccc;
      padding: 10px;
      text-align: center;
      cursor: pointer;
  }
  td.available {
      background-color: #c8e6c9; /* Green for available */
  }
  td.unavailable {
      background-color: #ffcdd2; /* Red for unavailable */
  }
</style>
<svelte:head>
    <title> HKN Portal | Interviews </title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</svelte:head>
<Layout>
  <div style="width: 95%; display: flex; align-items: center; justify-content: space-between;">
    <h1 style="margin-left: 15px">Interview Availability</h1>
  </div>
  <table>
    <thead>
        <tr>
            <th>Time</th>
            {#each days as day}
                <th>{day}</th>
            {/each}
        </tr>
    </thead>
    <tbody>
        {#each timeSlots as time, rowIndex}
            <tr>
                <td>{time}:00</td>
                {#each days as _, colIndex}
                    <td 
                        class:available={availabilityMatrix[rowIndex][colIndex] === 1}
                        class:unavailable={availabilityMatrix[rowIndex][colIndex] === 0}
                        on:click={() => toggleAvailability(rowIndex, colIndex)}>
                    </td>
                {/each}
            </tr>
        {/each}
    </tbody>

    <button on:click={submitAvailability}>Submit Availability</button>
  </table>
</Layout>