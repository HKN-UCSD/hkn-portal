<script>
    import { getEvent } from "../../Components/Events/eventstore";
    import { onMount } from "svelte";
    import { readable, writable } from "svelte/store";
    export let id;

    export const functionStore = writable({
        getAttendees: async(event) => {
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
        },

        getOutreachStudents: async() => {
            let response = await fetch(`/api/outreach/`);
            return await response.json();
        },
        getUsers: async() => {
            let response = await fetch(`/api/users/`);
            return await response.json();
        },
    })

    export const varStore = writable({
        event: null,
        attendees: [],
        outreachStudents: [],
        users: [],
    })

    const { getAttendees, getOutreachStudents, getUsers } = $functionStore;

    let drivers = [];
    let passengers = [];

    const loading = readable(true, (set) => {
        onMount(async () => {
            const event = await getEvent(id);
            const attendees = await getAttendees(event);
            const outreachStudents = await getOutreachStudents();
            const users = await getUsers();

            varStore.update(() => ({
                event,
                attendees,
                outreachStudents,
                users,
            }));

            if (attendees) {
                for (let attendee of attendees) {
                    let user = users.find(s => s.user_id === attendee);
                    if (user) {
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
    <!-- Drag and Drop script -->
    <script>
        async function getUsers() {
            let response = await fetch(`/api/users/`);
            return await response.json();
        }

        function drag(ev) {
            ev.dataTransfer.setData("id", ev.target.id);
            ev.dataTransfer.setData("origin", ev.target.parentNode.id);
        }

        function allowDrop(ev) {
            ev.preventDefault();
        }

        function drop(ev) {
            ev.preventDefault();
            let element_id = ev.dataTransfer.getData("id");
            let element = document.getElementById(element_id);
            if (ev.target.nodeName != "P") {
                console.log("not p element");
                ev.target.appendChild(element);
            }
        }

        function dropCar(ev) {
            ev.preventDefault();
            if (ev.target.nodeName != "P") {
                console.log("not p element");
                let element_id = ev.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (element.getAttribute("hasCar") == "true") {
                    ev.target.appendChild(element);
                } else {
                    let origin_id = ev.dataTransfer.getData("origin");
                    let origin = document.getElementById(origin_id);
                    origin.appendChild(element);
                }
            }
        }

        function dropNoCar(ev) {
            ev.preventDefault();
            if (ev.target.nodeName != "P") {
                console.log("not p element");
                let element_id = ev.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (element.getAttribute("hasCar") == "false") {
                    ev.target.appendChild(element);
                } else {
                    let origin_id = ev.dataTransfer.getData("origin");
                    let origin = document.getElementById(origin_id);
                    origin.appendChild(element);
                }
            }
        }

        function dropNewPool(ev) {
            ev.preventDefault();
            let element_id = ev.dataTransfer.getData("id");
            let element = document.getElementById(element_id);
            if (element.getAttribute("hasCar") == "true") {
                // create new element
                let newCarPool = document.createElement("div");
                newCarPool.style.cssText = `
                    outline: 2px solid black;
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    margin: 10px;
                    padding: 5px;
                    `;
                
                let driverHeading = document.createElement("p");
                driverHeading.style.cssText = `
                    font-size: 20px;
                    font-weight: bold;
                    margin: 5px 5px 5px 5px;
                    `;
                driverHeading.innerHTML = "Driver";
                newCarPool.appendChild(driverHeading);

                let driverBox = document.createElement("div");
                driverBox.setAttribute("ondrop", "dropCar(event)");
                driverBox.setAttribute("ondragover", "allowDrop(event)");
                driverBox.style.cssText = `
                    display: flex;
                    flex-direction: column;
                    min-height: 20px;
                `;
                driverBox.appendChild(element);
                newCarPool.appendChild(driverBox);

                let passengerHeading = document.createElement("p");
                passengerHeading.style.cssText = `
                    font-size: 20px;
                    font-weight: bold;
                    margin: 5px 5px 5px 5px;
                    `;
                passengerHeading.innerHTML = "Passengers";
                newCarPool.appendChild(passengerHeading)

                let passengerBox = document.createElement("div");
                passengerBox.setAttribute("ondrop", "drop(event)");
                passengerBox.setAttribute("ondragover", "allowDrop(event)");
                passengerBox.style.cssText = `
                    display: flex;
                    flex-direction: column;
                    min-height: 20px;
                `;
                newCarPool.appendChild(passengerBox);

                let ridesContainer = document.getElementById("rides");
                ridesContainer.insertBefore(newCarPool, ridesContainer.firstChild);
            } else {
                document.getElementById("noCars").appendChild(element);
            }
        }
    </script>
    <main>
        <div id="page">
            <!-- Left part of page to display every RSVP'd person -->
            <section id="people">
                <h2>Drivers</h2>
                <section id="cars" ondrop="dropCar(event)" ondragover="allowDrop(event)">
                    {#each drivers as driver}
                        <p class="attendee" id="{driver.email}" hasCar="true" draggable="true" ondragstart="drag(event)"> {driver.first_name} {driver.last_name} ({driver.email})</p>
                    {/each}
                    <p id="yyc003@ucsd.edu" hasCar="true" draggable="true" ondragstart="drag(event)"> Ryan Chen (yyc003@ucsd.edu) </p>
                </section>
                <h2>Attendees</h2>
                <section id="noCars" ondrop="dropNoCar(event)" ondragover="allowDrop(event)">
                    {#each passengers as passenger}
                        <p class="attendee" id="{passenger.email}" hasCar="false" draggable="true" ondragstart="drag(event)"> {passenger.first_name} {passenger.last_name} ({passenger.email})</p>
                    {/each}
                </section>
            </section>

            <!-- Right part of page to plan out rides -->
            <section id="rides">
                <!-- Create new "CarBox" when a driver is dropped into this box-->
                <div id="newCarBox" ondrop="dropNewPool(event)" ondragover="allowDrop(event)">
                    <p style="text-align:center; color: white;">Drop drivers here to create a new carpool</p>
                </div>
            </section>
        </div>
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
        margin: 10px;
        height: 50vh;
    }
    #noCars{
        outline: 1px solid red;
        margin: 10px;
        height: 50vh;
    }
    #rides{
        display: flex;
        flex-direction: column;
        align-content: center;
    }
    #newCarBox{
        outline: 2px solid black;
        border-radius: 10px;
        background-color: #099c30;
        opacity: 0.7;
        display: flex;
        margin: 10px 10px 10px 10px;
        width: 200px;
        height: 50px;
        justify-content: center;
        align-content: center;
    }
    .attendee{
        outline: 1px solid black;
        border-radius: 5px;
    }
    h2{
        margin: 10px;
    }
    p{
        margin: 5px;
    }
</style>