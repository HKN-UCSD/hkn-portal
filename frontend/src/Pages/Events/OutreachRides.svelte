<script>
    import { getEvent } from "../../Components/Events/eventstore";
    import { onMount } from "svelte";
    import { readable, writable } from "svelte/store";
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

    let drivers = [];
    let passengers = [];
    
    const loading = readable(true, (set) => {
        onMount(async () => {
            const event = await getEvent(id);
            const attendees = await getAttendees(event);
            const outreachStudents = await getOutreachStudents();
            const users = await getUsers();

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
        }

        function allowDrop(ev) {
            ev.preventDefault();
        }

        function drop(ev) {
            ev.preventDefault();
            let element_id = ev.dataTransfer.getData("id");
            let element = document.getElementById(element_id);
            if (ev.target.nodeName != "P") {
                ev.target.appendChild(element);
            }
        }

        function dropCar(ev) {
            ev.preventDefault();
            if (ev.target.nodeName != "P") {
                let element_id = ev.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (element.getAttribute("hasCar") == "true") {
                    ev.target.appendChild(element);
                } else {
                    let passengerBox = document.getElementById("passengers");
                    passengerBox.appendChild(element);
                }
            }
        }

        function dropNoCar(ev) {
            ev.preventDefault();
            if (ev.target.nodeName != "P") {
                let element_id = ev.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (element.getAttribute("hasCar") == "false") {
                    ev.target.appendChild(element);
                } else {
                    let driverBox = document.getElementById("drivers");
                    driverBox.appendChild(element);
                }
            }
        }

        // Create a new carPool when a driver is dropped onto the newCarBox
        // Parameter: ev (event)
        // Output: A new carPool div with the driver already appended
        let counter = 1;
        function dropNewPool(ev) {
            ev.preventDefault();
            let element_id = ev.dataTransfer.getData("id");
            let element = document.getElementById(element_id);
            if (element.getAttribute("hasCar") == "true") {
                // create new element
                let newCarPool = document.createElement("div");
                newCarPool.setAttribute("id", `carPool${counter}`);
                newCarPool.style.cssText = `
                    outline: 2px solid black;
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    margin: 10px;
                    padding: 5px;
                    `;

                let deleteButton = document.createElement("button");
                deleteButton.setAttribute("class", "");
                deleteButton.setAttribute("onclick", `deleteCarPool(carPool${counter})`);
                deleteButton.innerHTML = "x";
                deleteButton.style.cssText = `
                    position: relative;
                    top: 0;
                    bottom: 0;
                    background-color: red;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    cursor: pointer;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                `;
                newCarPool.appendChild(deleteButton);
                counter++;

                let driverHeading = document.createElement("p");
                driverHeading.style.cssText = `
                    font-size: 20px;
                    font-weight: bold;
                    margin: 5px;
                    `;
                driverHeading.innerHTML = "Driver";
                newCarPool.appendChild(driverHeading);

                let driverBox = document.createElement("div");
                driverBox.setAttribute("id", "driverBox");
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
                    margin: 5px;
                    `;
                passengerHeading.innerHTML = "Passengers";
                newCarPool.appendChild(passengerHeading)

                let passengerBox = document.createElement("div");
                passengerBox.setAttribute("id", "passengerBox");
                passengerBox.style.cssText = `
                    display: flex;
                    flex-direction: column;
                    min-height: 20px;
                `;

                let addPassenger = document.createElement("div");
                addPassenger.setAttribute("ondrop", "addPassenger(event)");
                addPassenger.setAttribute("ondragover", "allowDrop(event)");
                addPassenger.style.cssText = `
                    align-self: center;
                    outline: 2px solid black;
                    border-radius: 10px;
                    background-color: #099c30;
                    opacity: 0.7;
                    display: flex;
                    margin: 10px;
                    width: 200px;
                    height: 30px;
                    justify-content: center;
                `;
                let addPassengerText = document.createElement("p");
                addPassengerText.innerHTML = "Add passengers";
                addPassengerText.style.cssText = `
                    align-self: center;
                    text-align: center;
                    color: white;
                `;
                addPassenger.appendChild(addPassengerText);
                
                passengerBox.appendChild(addPassenger);
                newCarPool.appendChild(passengerBox);

                let ridesContainer = document.getElementById("rides");
                ridesContainer.insertBefore(newCarPool, ridesContainer.firstChild);
            } else {
                document.getElementById("passengers").appendChild(element);
            }
        }

        // Add a passenger to the carPool
        // Parameter: ev (event)
        function addPassenger(ev) {
            ev.preventDefault();
            let element_id = ev.dataTransfer.getData("id");
            let element = document.getElementById(element_id);
            let passengerBox = document.getElementById("passengerBox");
            passengerBox.insertBefore(element, passengerBox.firstChild);
        }

        // Delete the carPool when delete button is clicked
        // Parameter: carPool (HTML element)
        function deleteCarPool(carPool) {
            carPool.remove();
            while (carPool.firstElementChild !== null) {
                let element = carPool.firstElementChild;
                element.remove();
                while (element.firstElementChild != null) {
                    let child = element.firstElementChild;
                    child.remove();
                    if (child.classList.contains("attendee")) {
                        if (child.getAttribute("hasCar") == "true") {
                            document.getElementById("drivers").appendChild(child);
                        } else {
                            document.getElementById("passengers").appendChild(child);
                        }
                    }
                }
            }
        }
    </script>
    <main>
        <div id="page">
            <!-- Left part of page to display every RSVP'd person -->
            <section id="people">
                <h2>Drivers</h2>
                <section id="drivers" ondrop="dropCar(event)" ondragover="allowDrop(event)">
                    {#each drivers as driver}
                        <p class="attendee" id="{driver.email}" hasCar="true" draggable="true" ondragstart="drag(event)"> {driver.first_name} {driver.last_name} ({driver.email})</p>
                    {/each}
                    <p class="attendee" id="yyc003@ucsd.edu" hasCar="true" draggable="true" ondragstart="drag(event)"> Ryan Chen (yyc003@ucsd.edu) </p>
                    <p class="attendee" id="meghaj" hasCar="true" draggable="true" ondragstart="drag(event)"> Meghaj (email) </p>
                </section>
                <h2>Attendees</h2>
                <section id="passengers" ondrop="dropNoCar(event)" ondragover="allowDrop(event)">
                    {#each passengers as passenger}
                        <p class="attendee" id="{passenger.email}" hasCar="false" draggable="true" ondragstart="drag(event)"> {passenger.first_name} {passenger.last_name} ({passenger.email})</p>
                    {/each}
                </section>
            </section>

            <!-- Right part of page to plan out rides -->
            <section id="rides">
                <!-- Create new "CarBox" when a driver is dropped into this box-->
                <div id="newCarBox" ondrop="dropNewPool(event)" ondragover="allowDrop(event)">
                    <p style="text-wrap: balance; text-align:center; color: white;">Drop drivers here to create a new carpool</p>
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
    #drivers{
        outline: 1px solid red;
        margin: 10px;
        height: 50vh;
    }
    #passengers{
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
        margin: 10px;
        width: 260px;
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