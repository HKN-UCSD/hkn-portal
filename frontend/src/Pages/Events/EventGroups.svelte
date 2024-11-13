<script>
    import { getEvent } from "../../Components/Events/eventstore";
    import { onMount, tick } from "svelte";
    import { readable } from "svelte/store";
    import Layout from "../../Layout.svelte";
    export let id;

    // Function to get all RSVP'd users for the event
    // Parameter: event (the event's id)
    // Output: A list of RSVP'd attendees' user id
    async function getAttendees(event) {
        let response = await fetch(`/api/eventactionrecords/`);
            if (response.status == 200) {
                let records = await response.json();
                let attendees = [];

                // Filter records for RSVP's related to this event
                for (let record of records) {
                    if (record.event == event.pk && record.action == "RSVP") {
                        attendees.push(record.acted_on);
                    }
                }
                return attendees;
            } else {
                throw new Error(response.statusText);
            }
    }

    // Function to get all OutreachStudent objects
    // Parameter: none
    // Output: List of all OutreachStudent
    async function getOutreachStudents() {
        let response = await fetch(`/api/outreach/`);
        return await response.json();
    }

    // Function to get all Users objects
    // Parameter: none
    // Output: List of all Users
    async function getUsers() {
        let response = await fetch(`/api/users/`);
        return await response.json();
    }

    // Save user information of attendees
    let userAttendees = [];
    let selectedLeaders = [];
    let isLoading = true;

    $: console.log("Selected Leaders:", selectedLeaders); // for monitoring changes in selectedLeaders

    onMount(async () => {
        try {
            const event = await getEvent(id);
            const [attendees, users] = await Promise.all([
                getAttendees(event),
                getUsers(),
            ]);

            if (attendees) {
                for (let attendee of attendees) {
                    let user = users.find(user => user.user_id == attendee);
                    userAttendees.push(user);
                }
            }
        } finally {
            isLoading = false;
        }
        
    });

    // Handle checkbox selection
    function toggleSelection(attendeeId) {
        if (selectedLeaders.includes(attendeeId)) {
            selectedLeaders = selectedLeaders.filter(id => id !== attendeeId);
        } else {
            selectedLeaders = [...selectedLeaders, attendeeId];
        }
    }
</script>

<svelte:head>
    <title> HKN Portal | Group Assignment</title>
</svelte:head>

<Layout>
    <div class="group-assignment">
        {#if isLoading}
            <p>Loading...</p>
        {:else}
            <div>
                <h2>Select Group Leaders</h2>
                <div class="scroll-box">
                    {#each userAttendees as attendee}
                        <div class="checkbox-item">
                            <input
                                type="checkbox"
                                id={attendee.user_id}
                                value={attendee.user_id}
                                on:change={() => toggleSelection(attendee.user_id)}
                                checked={selectedLeaders.includes(attendee.user_id)}
                            />
                            <label for={attendee.user_id}>
                                {attendee.preferred_name} {attendee.last_name}
                            </label>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</Layout>

<style>
    .group-assignment {
        padding: 1rem;
    }

    .scroll-box {
        border: 1px solid #ccc;
        border-radius: 4px;
        height: 15rem;
        overflow-y: auto;
        padding: 0.5rem;
    }

    .checkbox-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .checkbox-item input[type="checkbox"] {
        margin-right: 0.5rem;
    }
</style>