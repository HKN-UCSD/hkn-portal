<script>
  import { onMount } from "svelte";
  import Layout from "../Layout.svelte";
  export let id;
  let userData = null;
  let userGroups = [];
  let self = false;
  let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  let availabilityMatrix = Array.from({ length: 11 }, () => Array(5).fill(0));
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
    
    /* for (let group of ["Inductee", "Member", "Outreach Student", "Officer"]) {
        if (userData[group]) {
          userGroups.push(group);
        }
    } */
  });

    // 2D array for availability (all set to 0 initially)
    
    // Toggle availability on cell click
  async function toggleAvailability(row, col) {
    availabilityMatrix[row][col] = 1 - availabilityMatrix[row][col]; // Toggle between 1 and 0
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

    pastEvents.sort((a,b) => 
        (new Date(b.start_time)) - (new Date(a.start_time))
    );

    for (let event of pastEvents) {
        let eventStartTime = new Date(event.start_time)
        event.date = eventStartTime.toLocaleString(undefined, {
          timeszone: 'UTC',
          dateStyle: 'long',
        });
    }

    return pastEvents;
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

    <button>Submit Availability</button>
  </table>
</Layout>