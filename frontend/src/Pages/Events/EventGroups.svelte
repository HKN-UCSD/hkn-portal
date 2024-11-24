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

    // Generate a JSON representation of created tourGroups
    // Parameters: None
    // Output: JSON in the format {tourGroups: {tourLead: email, nonTourLeads: [list of emails]}, ...}
    function getGroups() {
        let tourGroups = Object.create(null);
        let tourGroupsContainer = document.getElementById("tourGroups");
        let tourGroupsCount = 1;

        // Iterate through each element of rides section
        for (let tourGroup of tourGroupsContainer.children) {
            let thisPool = Object.create(null);
            let nonTourLeads = [];

            // Iterate through elements of tourGroup
            for (let element of tourGroup.children) {
                    // tourGroup's driver
                    if (element.classList.contains("tourLeadsBox")) {
                        if (element.firstChild != null) {
                            thisPool["tourLead"] = `${element.firstChild.innerHTML} (${element.firstChild.getAttribute("id")})`;
                        } else {
                            thisPool["tourLead"] = "";
                        }
                    }
                    // tourGroup's passengers
                    else if (element.classList.contains("nonTourLeadsBox")) {
                        for (let attendee of element.children) {
                            if (attendee.classList.contains("attendee")) {
                                passengers.push(`${attendee.innerHTML} (${attendee.getAttribute("id")})`);
                            }
                        }
                        thisPool["nonTourLead"] = passengers;
                    }
                }

            // Add thisPool to dictionary of tourGroup
            tourGroups[`tourGroup${tourGroupsCount}`] = thisPool;
            tourGroupsCount++;
        }
        return tourGroups;
    }

    async function save(event) {
        //to be implemented
    }
    async function loadrides(){

    }

    // Save user information of attendees
    let userAttendees = [];
    let tourLeads = [];
    let isLoading = true;
    let tourAttendees = []
    $: console.log("Selected Leaders:", tourLeads); // for monitoring changes in selectedLeaders

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
        if (tourLeads.includes(attendeeId)) {
            tourLeads = tourLeads.filter(id => id !== attendeeId);
        } else {
            tourLeads = [...tourLeads, attendeeId];
        }
    }

    
</script>

<svelte:head>
    <title> HKN Portal | Group Assignment</title>
</svelte:head>

<Layout>
    <main>
        <style>
            #eventLink{
                    color: white;
                    margin-left: 15px;
                    margin-bottom: 20px;
                    border-radius: 0.25em;
                    padding: 0.4em 0.65em;
                    background-color: var(--fc-button-bg-color);
                    border: none;
                    outline: none;
            }
            select {
                width: 100%;
                height: 10rem;
            }
            h2{
                margin: 10px;
            }
            #drag-n-drop-section{
                    display: flex;
                    flex-direction: row;
                    height: 90vh;
                    margin-top: 10px;
                    margin-left: 15px;
            }
            #event-attendees-section{
                display: flex;
                flex-direction: column;
                padding: 5px 5px;
                border-radius: 5px;
                box-shadow: 0px 1px 2px 1px lightgrey;
                grid-area: c;
                background-color: #f5f5f5;
                height: 88vh;
                width: 18vw;
            }
            #tour-leads{
                margin: 10px;
                padding: 5px 5px;
                border-radius: 5px;
                box-shadow: 0px 1px 2px 1px lightgrey;
                grid-area: c;
                background-color: #e3e3e3;
                width: 15vw;
                height: 50%;
                overflow: auto;
            }
            #tour-attendees{
                margin: 10px;
                padding: 5px 5px;
                border-radius: 5px;
                box-shadow: 0px 1px 2px 1px lightgrey;
                grid-area: c;
                background-color: #e3e3e3;
                width: 15vw;
                height: 50%;
                overflow: auto;
            }
            .attendee{
                outline: 1px solid black;
                padding: 5px;
                border-radius: 5px;
                background-color: #f1f1f1;
                cursor: grabbing;
            }
            #assigned-groups-section{
                display: flex;
                margin: 0px 0px 0px 10px;
                padding: 5px 5px;
                border-radius: 5px;
                box-shadow: 0px 1px 2px 1px lightgrey;
                background-color: #f5f5f5;
                height: 88vh;
                width: 55vw;
                flex-direction: column;
            }
            #assigned-groups{
                display: flex;
                width: 55vw;
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: flex-start;
            }
            #functions{
                display: flex;
                width: 55vw;
                flex-direction: column;
                justify-content: flex-start;
            }
            #newGroupDropBox{
                margin: 10px 15px 10px 15px;
                border-radius: 10px;
                outline: 2px solid black;
                background-color: #099c30;
                opacity: 0.7;
                display: flex;
                width: 15vw;
                justify-content: center;
            }
            .instructionText{
                text-wrap: balance;
                align-self: center;
                text-align: center;
                color: white;
            }
            #saveButton{
                margin: 10px 15px 10px 15px;
                border-radius: 10px;
                width: 15vw;
            }
        </style>
        {#if isLoading}
            <p>Loading...</p>
        {:else if userAttendees.length === 0}
            <p>No attendees have RSVP'd for this event.</p>
        {:else}
            <a id="eventLink" href="/events/{id}"> Back to Event</a>
            <div class="select-leaders">
                <h2>Select Group Leaders</h2>
                <!-- Create a scoll box to list out all attendees. Select the box to make them tour leaders. -->
                <div class="scroll-box">
                    {#each userAttendees as attendee}
                        <div class="checkbox-item">
                            <input
                                type="checkbox"
                                id={attendee.user_id}
                                value={attendee.user_id}
                                on:change={() => toggleSelection(attendee.user_id)}
                                checked={tourLeads.includes(attendee.user_id)}
                            />
                            <label for={attendee.user_id}>
                                {attendee.preferred_name} {attendee.last_name}
                            </label>
                        </div>
                    {/each}
                </div>
            </div>

            <div id="drag-n-drop-section">
                <!-- Left part of page to display every attendee -->
                <section id="event-attendees-section">
                    <h2>Tour Leads</h2>
                    <section id="tour-leads" ondrop="dropCar(event)" ondragover="allowDrop(event)">
                        {#each tourLeads as tourLead}
                            <p class="attendee" id="{tourLead.email}" hasCar="true" draggable="true" ondragstart="drag(event)"> {tourLead.preferred_name} {tourLead.last_name}</p>
                        {/each} 
                    </section>
                    <h2>Tour Attendees</h2>
                    <section id="tour-attendees" ondrop="dropNoCar(event)" ondragover="allowDrop(event)">
                        {#each tourAttendees as tourAttendee}
                            <p class="attendee" id="{tourAttendee.email}" hasCar="false" draggable="true" ondragstart="drag(event)"> {tourAttendee.preferred_name} {tourAttendee.last_name}</p>
                        {/each}
                    </section>
                </section>
                <!-- Right part of page to plan rides -->
                <section id="assigned-groups-section">
                    <section id="assigned-groups" onload="loadRides()">
                        <!-- Create and add new "tour-groups"s in this section -->
                    </section>
                    <script>
                        // Grab JSON
                        // Create carPools and add to carPools if JSON has data
                        // Remember to remove from list before adding to new carPool
                        // Keep counterCount? and remember to increment
                    </script>
                    <section id="functions">
                        <div id="newGroupDropBox" ondrop="dropNewPool(event)" ondragover="allowDrop(event)">
                            <p class="instructionText">Drop tour leads here to create a new tour group</p>
                        </div>    
                        <form on:submit={save}>
                            <button id="saveButton"> Save </button>
                        </form>
                    </section>
                </section>
            </div>
        {/if}
        
    </main>
</Layout>

<style>
    main{ 
        padding: 1rem;
    }
    .scroll-box {
        border-radius: 5px;
        height: 10rem;
        overflow-y: auto;
        padding: 0.5rem;
        box-shadow: 0px 1px 2px 1px lightgrey;
        grid-area: c;
        background-color: #f5f5f5;
        margin-left: 15px;
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