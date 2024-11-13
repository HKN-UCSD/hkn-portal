<script>
    import { getEvent } from "../../Components/Events/eventstore";
    // import { populateFormToUpdateRides } from "../../Components/Events/eventutils"
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

    // Generate a JSON representation of created carPools
    // Parameters: None
    // Output: JSON in the format {carPool1: {driver: email, passengers: [list of emails]}, ...}
    function getGroups() {
        let groups = Object.create(null);
        let groupsContainer = document.getElementById("groupsContainer");
        let groupCount = 1;

        // Iterate through each group
        for (let group of groupsContainer.children) {
            let thisGroup = Object.create(null);
            let participants = [];

            // Iterate through elements of each group
            for (let element of group.children) {
                // Group's tour guide
                if (element.classList.contains("tourGuideBox")) {
                    if (element.firstChild != null) {
                        thisGroup["tourGuide"] = `${element.firstChild.innerHTML} (${element.firstChild.getAttribute("id")})`;
                    } else {
                        thisGroup["tourGuide"] = "";
                    }
                }
                // Group's participants
                else if (element.classList.contains("participantBox")) {
                    for (let attendee of element.children) {
                        if (attendee.classList.contains("attendee")) {
                            participants.push(`${attendee.innerHTML} (${attendee.getAttribute("id")})`);
                        }
                    }
                    thisGroup["participants"] = participants;
                }
            }

            // Add this group to dictionary of groups
            groups[`group${groupCount}`] = thisGroup;
            groupCount++;
        }
        return groups;
    }

    async function save(event) {
        event.preventDefault();

        const groups = JSON.stringify(getGroups());  // Use getGroups instead of getRides
        const formData = await populateFormToUpdateGroups(id, groups);  // Update form handling for groups

        const CSRFToken = document.cookie
            .split("; ")
            .find((element) => element.startsWith("csrftoken="))
            .split("=")[1];
        formData.set("csrfmiddlewaretoken", CSRFToken);

        const response = await fetch(`/api/events/${id}/`, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': CSRFToken,
            },
            body: new URLSearchParams(formData),
        });
        if (response.ok) {
            alert("Saved");
        } else {
            alert(`Unable to save. Response status ${response.status}`);
        };
    }

    //Assign team leads
    let teamLeads = new Set();;

    function toggleTeamLead(attendeeId) {
        if (teamLeads.includes(attendeeId)) {
            teamLeads = teamLeads.filter(id => id !== attendeeId);
        } else {
            teamLeads.push(attendeeId);
        }
    }

    // Fetch all necessary data on component mount
    onMount(async () => {
        const event = await getEvent(id);
        [attendees, outreachStudents, users] = await Promise.all([
            getAttendees(event),
            getOutreachStudents(),
            getUsers(),
        ]);
    });

</script>

<svelte:head>
    <title> HKN Portal | Group Assignment</title>
</svelte:head>

<Layout>
    <div id="attendeesList">
        {#each attendees as attendee}
            <div>
                <input 
                    type="checkbox" 
                    id={attendee.id} 
                    on:change={() => toggleTeamLead(attendee.id)} 
                />
                <label for={attendee.id}>{attendee.name}</label>
            </div>
        {/each}
    </div>
</Layout>