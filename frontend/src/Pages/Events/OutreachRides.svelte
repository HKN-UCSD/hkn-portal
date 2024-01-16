<script>
    import { loop_guard } from "svelte/internal";
    import { getEvent } from "../../Components/Events/eventstore";
    import { onMount } from "svelte";
    import { readable } from "svelte/store";
    export let id;

    async function getAttendees(event) {
        let response = await fetch(`/api/eventactionrecords/`);
        if (response.status == 200) {
            // filter for RSVP records related to this event
            let records = await response.json();
            let attendees = [];
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

    async function getOutreachStudents() {
        let response = await fetch(`/api/outreach/`);
        return await response.json();
    }

    async function getUsers() {
        let response = await fetch(`/api/users/`);
        return await response.json();
    }

    // Grab all attendees and outreach students
    // Sort into 2 lists: drivers and passengers
    let drivers = [];
    let passengers = [];
    let event;
    let attendees;
    let outreachStudents;
    let users;

    const loading = readable(true, (set) => {
        onMount(async () => {
            event = await getEvent(id);
            attendees = await getAttendees(event);
            outreachStudents = await getOutreachStudents();
            users = await getUsers();

            if (attendees) {
                for (let attendee of attendees) {
                    console.log(attendee);
                    let user = users.find(s => s.user_id === attendee);
                    if (user) {
                        console.log(user);
                        console.log(user.first_name);
                        if (outreachStudents.includes(attendee)) {
                            let student = outreachStudents.find(s => s.id === attendee.id)
                            if (student.car == "Yes") {
                                drivers.push(user);
                            } else {
                                passengers.push(user);
                            }
                        } else {
                            passengers.push(user);
                        }
                    }
                }
            }

            set(false);
        });
    });
</script>

<svelte:head>
    <title> HKN Portal | Ride Assignment</title>
</svelte:head>

{#if $loading}
    <p>Loading...</p>
{:else}
    <main>
        <div id = "page">
            <!-- Left part of page to display every RSVP'd person -->
            <section id = "people">
                <section id = "cars" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <h2>Drivers</h2>
                    {#each drivers as driver}
                        <p id="car" draggable="true" ondragstart="drag(event)"> {driver.first_name} {driver.last_name} ({driver.email})</p>
                    {/each}
                </section>
                <section id = "no_cars" ondrop="drop(event)" ondragover="allowDrop(event)">
                    <h2>Attendees</h2>
                    {#each passengers as passenger}
                        <p id="car" draggable="true" ondragstart="drag(event)"> {passenger.first_name} {passenger.last_name} ({passenger.email})</p>
                    {/each}
                </section>
            </section>

            <!-- Right part of page to plan out rides -->
            <section id = "rides">
                <!-- Create new "CarBox" when a driver is dropped into this box-->
                <div id = "newCarBox" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                <script> 
                    // on drop create new box with the name of the driver
                </script>
            </section>
        </div>

        <!-- Drag and Drop script -->
        <script>
            function allowDrop(ev) {
            ev.preventDefault();
            }
            function drag(ev) {
            
            ev.dataTransfer.setData("text", ev.target.id);
            }
            function drop(ev) {
            ev.preventDefault();
            let data = ev.dataTransfer.getData("text");
            ev.target.appendChild(document.getElementById(data));
            }
        </script>
    </main>
{/if}


<style>
    #page{
        outline: 1px solid red;
        display: flex;
        flex-direction: row;
        height: 100vh;
        width: 100vw;
    }
    #people{
        align-self: left;
        outline: 1px solid red;
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: 25vw;
    }
    #cars{
        outline: 1px solid red;
        margin: 10px 0px 0px 10px;
        height: 50vh;
    }
    #no_cars{
        outline: 1px solid red;
        margin: 10px 0px 0px 10px;
        height: 50vh;
    }
    #newCarBox{
        outline: 1px solid blue;
        margin: 10px 0px 0px 10px;
        width: 200px;
        height: 50px;
    }
</style>