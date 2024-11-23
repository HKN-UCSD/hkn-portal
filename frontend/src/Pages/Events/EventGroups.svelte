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

    async function save(event) {
        //to be implemented
    }
    async function loadrides(){

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
            .group-assignment {
                padding: 1rem;
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
        {:else}
            <div>
                <h2>Select Group Leaders</h2>
                <div>
                    <select bind:value={selectedLeaders} multiple>
                        {#each userAttendees as attendee}
                            <option>{attendee.preferred_name} {attendee.last_name}</option>
                        {/each}
                    </select>
                </div>
            </div>
        {/if}
    </main>
</Layout>

<style>
    .group-assignment {
        padding: 1rem;
    }

    select {
        width: 100%;
        height: 10rem;
    }
</style>