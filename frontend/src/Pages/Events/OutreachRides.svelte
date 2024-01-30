<script>
    import { getEvent } from "../../Components/Events/eventstore";
    import { populateFormToUpdateRides } from "../../Components/Events/eventutils"
    import { onMount, tick } from "svelte";
    import { readable } from "svelte/store";
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
    function getRides() {
        let carPools = Object.create(null);
        let carPoolsContainer = document.getElementById("carPools");
        let carPoolsCount = 1;

        // Iterate through each element of rides section
        for (let carPool of carPoolsContainer.children) {
            let thisPool = Object.create(null);
            let passengers = [];

            // Iterate through elements of carPool
            for (let element of carPool.children) {
                    // carPool's driver
                    if (element.classList.contains("driverBox")) {
                        if (element.firstChild != null) {
                            thisPool["driver"] = `${element.firstChild.innerHTML} (${element.firstChild.getAttribute("id")})`;
                        } else {
                            thisPool["driver"] = "";
                        }
                    }
                    // carPool's passengers
                    else if (element.classList.contains("passengerBox")) {
                        for (let attendee of element.children) {
                            if (attendee.classList.contains("attendee")) {
                                passengers.push(`${attendee.innerHTML} (${attendee.getAttribute("id")})`);
                            }
                        }
                        thisPool["passengers"] = passengers;
                    }
                }

            // Add thisPool to dictionary of carPools
            carPools[`carPool${carPoolsCount}`] = thisPool;
            carPoolsCount++;
        }
        return carPools;
    }

    // Save created carpools so that progress is not reset when refreshing page
    // Parameter: id (event id)
    // Output: Save carpools in JSON string under the event
    async function save(event) {
        event.preventDefault();

        const carPools = JSON.stringify(getRides());
        const formData = await populateFormToUpdateRides(id, carPools);

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

    // Function that gets called when the page first loads in.
    // Split attendees into drivers and passengers depending on whether they have a car.
    // Parameter: none
    // Output: Two lists: drivers and passengers
    let drivers = [];
    let passengers = [];
    
    // Use loading tag to stop page from loading until this is complete
    const loading = readable(true, (set) => {
        function parseEmail(attendee) {
            console.log(attendee);
            return attendee.split("(")[1].split(")")[0];
        }

        onMount(async () => {
            const event = await getEvent(id);
            const [attendees, outreachStudents, users] = await Promise.all([
                getAttendees(event),
                getOutreachStudents(),
                getUsers(),
            ]);

            if (attendees) {
                for (let attendee of attendees) {
                    // Find user object of attendee
                    let user = users.find(user => user.user_id == attendee);
                    if (user) {
                        let outreachStudent = outreachStudents.find(student => student.user_id == attendee);
                        if (outreachStudent) {
                            // Sort users into drivers and passenger
                            if (outreachStudent.car == "Yes") {
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

            // Finished loading, set to false
            set(false);

            await tick();
            // Load saved rides            
            let counter = 1;
            for (const key in event.rides) {
                // Create new carPool
                let newCarPool = document.createElement("div");
                    newCarPool.setAttribute("id", `carPool${counter}`);
                    newCarPool.setAttribute("class", "carPool");

                // Create delete button
                let deleteButton = document.createElement("button");
                    deleteButton.setAttribute("onclick", `deleteCarPool(carPool${counter})`);
                    deleteButton.setAttribute("id", "deleteButton");
                    deleteButton.innerHTML = "x";

                // Create driver section heading
                let driverHeading = document.createElement("p");
                    driverHeading.setAttribute("class", "poolSectionHeading");
                    driverHeading.innerHTML = "Driver";

                // Create box for drivers
                let driverBox = document.createElement("div");
                    driverBox.setAttribute("id", `driverBox${counter}`);
                    driverBox.setAttribute("class", `driverBox`);
                    driverBox.setAttribute("ondrop", `addDriver(event, driverBox${counter})`);
                    driverBox.setAttribute("ondragover", "allowDrop(event)");

                // Create passenger section heading
                let passengerHeading = document.createElement("p");
                    passengerHeading.setAttribute("class", "poolSectionHeading");
                    passengerHeading.innerHTML = "Passengers";

                // Create box for passengers
                let passengerBox = document.createElement("div");
                    passengerBox.setAttribute("id", `passengerBox${counter}`);
                    passengerBox.setAttribute("class", "passengerBox");

                // Create instruction for adding passengers
                let addPassengerSign = document.createElement("div");
                    addPassengerSign.setAttribute("ondrop", `addPassenger(event, passengerBox${counter})`);
                    addPassengerSign.setAttribute("class", "addPassengerSign");
                    addPassengerSign.setAttribute("ondragover", "allowDrop(event)");
                let addPassengerText = document.createElement("p");
                    addPassengerText.setAttribute("class", "instructionText");
                    addPassengerText.innerHTML = "Add passengers";

                // Construct carpool
                newCarPool.append(
                    deleteButton,
                    driverHeading,
                    driverBox,
                    passengerHeading,
                    passengerBox,
                );
                
                passengerBox.appendChild(addPassengerSign);
                addPassengerSign.appendChild(addPassengerText);

                // Insert driver and passengers
                if (event.rides[key]["driver"]) {
                    try {
                        const driverEmail = parseEmail(event.rides[key]["driver"]);
                        const driver = document.getElementById(driverEmail);
                        driverBox.appendChild(driver);
                    }
                    catch {
                    }
                }

                for (const attendee of event.rides[key]["passengers"]) {
                    try {
                        const passengerEmail = parseEmail(attendee);
                        const passenger = document.getElementById(passengerEmail);
                        passengerBox.insertBefore(passenger, passengerBox.lastChild);
                    }
                    catch {
                    }
                }

                // Add carpool to container
                let carPoolsContainer = document.getElementById("carPools");
                carPoolsContainer.appendChild(newCarPool);
                counter++;
            }
        });
    });
</script>

<svelte:head>
    <title> HKN Portal | Ride Assignment</title>
</svelte:head>

<main>
    <style>
        #page{
            display: flex;
            flex-direction: row;
            height: 90vh;
        }
        #attendees{
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
        #drivers{
            margin: 10px;
            padding: 5px 5px;
            border-radius: 5px;
            box-shadow: 0px 1px 2px 1px lightgrey;
            grid-area: c;
            background-color: #e3e3e3;
            width: 15vw;
            height: 50%;
        }
        #passengers{
            margin: 10px;
            padding: 5px 5px;
            border-radius: 5px;
            box-shadow: 0px 1px 2px 1px lightgrey;
            grid-area: c;
            background-color: #e3e3e3;
            width: 15vw;
            height: 50%;
        }
        #rides{
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
        #carPools{
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
        #newCarBox{
            margin: 10px 15px 10px 15px;
            border-radius: 10px;
            outline: 2px solid black;
            background-color: #099c30;
            opacity: 0.7;
            display: flex;
            width: 15vw;
            justify-content: center;
        }
        #saveButton{
            margin: 10px 15px 10px 15px;
            border-radius: 10px;
            width: 15vw;
        }
        .attendee{
            outline: 1px solid black;
            padding: 5px;
            border-radius: 5px;
            background-color: #f1f1f1;
            cursor: grabbing;
        }
        .carPool{
            outline: 2px solid black;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            margin: 10px;
            padding: 5px;
            width: 15vw;
        }
        #deleteButton{
            position: relative;
            top: 0;
            bottom: 0;
            background-color: red;
            color: white;
            border: none;
            border-radius: 50%;
            padding: 0px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .poolSectionHeading{
            font-size: 20px;
            font-weight: bold;
            margin: 5px;
        }
        .driverBox{
            display: flex;
            flex-direction: column;
            min-height: 20px;
        }
        .passengerBox{
            display: flex;
            flex-direction: column;
            min-height: 20px
        }
        .addPassengerSign{
            align-self: center;
            outline: 2px solid black;
            border-radius: 10px;
            background-color: #099c30;
            opacity: 0.7;
            display: flex;
            margin: 10px;
            width: 15vw;
            height: 30px;
            justify-content: center;
        }
        .instructionText{
            text-wrap: balance;
            align-self: center;
            text-align: center;
            color: white;
        }
        h2{
            margin: 10px;
        }
        p{
            margin: 5px;
        }
    </style>

    {#if $loading}
        <p>Loading...</p>
    {:else}
        <!-- Drag and Drop script -->
        <script context="module">
            // Transfers dragged item's id when starting drag
            function drag(event) {
                event.dataTransfer.setData("id", event.target.id);
                event.target.style.cursor = 'grabbing';
            }

            // Prevents default browser action (open link)
            function allowDrop(event) {
                event.preventDefault();
            }

            // Default drop function
            // Parameter: event
            // Output: Added dragged user to where it was dropped
            function drop(event) {
                event.preventDefault();
                let element_id = event.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (event.target.nodeName != "P") {
                    event.target.appendChild(element);
                }
            }

            // Process dragged and dropped user in the 'drivers' list
            // Parameter: event
            // Output: Added dragged user to 'drivers' list if driver
            //         added user to 'passengers' list if not driver
            function dropCar(event) {
                event.preventDefault();

                // Block inserting element into another 'p' element
                if (event.target.nodeName != "P") {
                    let element_id = event.dataTransfer.getData("id");
                    let element = document.getElementById(element_id);

                    // Check if user has car (is driver)
                    if (element.getAttribute("hasCar") == "true") {
                        event.target.appendChild(element);
                    } else {
                        let passengerBox = document.getElementById("passengers");
                        passengerBox.appendChild(element);
                    }
                }
            }

            // Process dragged and dropped user in the 'passengers' list
            // Parameter: event
            // Output: Added dragged user to 'passenger' list if not driver
            //         added user 'drivers' list if driver
            function dropNoCar(event) {
                event.preventDefault();

                // Block inserting element into another 'p' element
                if (event.target.nodeName != "P") {
                    let element_id = event.dataTransfer.getData("id");
                    let element = document.getElementById(element_id);

                    // Check if user has car (is driver)
                    if (element.getAttribute("hasCar") == "false") {
                        event.target.appendChild(element);
                    } else {
                        let driverBox = document.getElementById("drivers");
                        driverBox.appendChild(element);
                    }
                }
            }

            // Create a new carPool when a driver is dropped onto the newCarBox
            // Parameter: event
            // Output: A new carPool div with the driver already appended
            function dropNewPool(event) {
                event.preventDefault();

                // use a counter so created id's don't repeat
                let counter = document.getElementById("carPools").children.length + 1;

                let element_id = event.dataTransfer.getData("id");
                let element = document.getElementById(element_id);

                // Check if attendee is a driver
                if (element.getAttribute("hasCar") == "true") {
                    // Create new 'div' named 'carPool{counter}'
                    let newCarPool = document.createElement("div");
                        newCarPool.setAttribute("id", `carPool${counter}`);
                        newCarPool.setAttribute("class", "carPool");

                    // Create delete button for 'div'
                    let deleteButton = document.createElement("button");
                        deleteButton.setAttribute("onclick", `deleteCarPool(carPool${counter})`);
                        deleteButton.setAttribute("id", "deleteButton");
                        deleteButton.innerHTML = "x";

                    // Create driver section heading
                    let driverHeading = document.createElement("p");
                        driverHeading.setAttribute("class", "poolSectionHeading");
                        driverHeading.innerHTML = "Driver";

                    // Create box to drag and drop drivers into
                    let driverBox = document.createElement("div");
                        driverBox.setAttribute("id", `driverBox${counter}`);
                        driverBox.setAttribute("class", `driverBox`);
                        driverBox.setAttribute("ondrop", `addDriver(event, driverBox${counter})`);
                        driverBox.setAttribute("ondragover", "allowDrop(event)");

                    // Create passenger section heading
                    let passengerHeading = document.createElement("p");
                        passengerHeading.setAttribute("class", "poolSectionHeading");
                        passengerHeading.innerHTML = "Passengers";

                    // Create box to drag and drop passengers into
                    let passengerBox = document.createElement("div");
                        passengerBox.setAttribute("id", `passengerBox${counter}`);
                        passengerBox.setAttribute("class", "passengerBox");


                    // Create a 'div' to indicate to user where to drop passengers
                    let addPassengerSign = document.createElement("div");
                        addPassengerSign.setAttribute("ondrop", `addPassenger(event, passengerBox${counter})`);
                        addPassengerSign.setAttribute("class", "addPassengerSign");
                        addPassengerSign.setAttribute("ondragover", "allowDrop(event)");

                    // Create the text instructions for users
                    let addPassengerText = document.createElement("p");
                        addPassengerText.setAttribute("class", "instructionText");
                        addPassengerText.innerHTML = "Add passengers";

                    // Add all created elements to carpool
                    newCarPool.append(
                        deleteButton,
                        driverHeading,
                        driverBox,
                        passengerHeading,
                        passengerBox,
                    );

                    // Add dragged and dropped user as the driver
                    driverBox.appendChild(element);

                    passengerBox.appendChild(addPassengerSign);
                    addPassengerSign.appendChild(addPassengerText);

                    let carPoolsContainer = document.getElementById("carPools");
                    carPoolsContainer.appendChild(newCarPool);
                } else {
                    document.getElementById("passengers").appendChild(element);
                }
            }

            // Add a driver to the carPool's driverBox
            // Parameter: event, driverBox (container to add element to)
            // Output: Add dragged element to driverBox if there isn't already a driver
            function addDriver(event, driverBox) {
                event.preventDefault();
                let element_id = event.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                if (element.getAttribute("hasCar") == "true" && driverBox.children.length < 1) {
                    driverBox.appendChild(element);
                }
            }

            // Add a passenger to the carPool's passengerBox
            // Parameter: event, passengerBox (container to add element to)
            // Output: Add dragged element to passengerBox
            function addPassenger(event, passengerBox) {
                event.preventDefault();
                let element_id = event.dataTransfer.getData("id");
                let element = document.getElementById(element_id);
                passengerBox.insertBefore(element, passengerBox.lastChild);
            }

            // Delete the carPool when delete button is clicked
            // Parameter: carPool (HTML element)
            // Output: deleted carPool, all drivers/passengers returned to lists
            function deleteCarPool(carPool) {
                // Remove element from parent container 'rides'
                carPool.remove();
                for (let element of carPool.children) {
                    // Remove element from parent container 'carPool'
                    element.remove();

                    // Clone array so for loop does not get affected
                    let children = Array.from(element.children);
                    for (let child of children) {
                        // Remove element from parent container 'driverBox' or 'passengerBox'
                        child.remove();

                        // Append to drivers or passengers depending on hasCar
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
                <!-- Left part of page to display every attendee -->
                <section id="attendees">
                    <h2>Drivers</h2>
                    <section id="drivers" ondrop="dropCar(event)" ondragover="allowDrop(event)">
                        {#each drivers as driver}
                            <p class="attendee" id="{driver.email}" hasCar="true" draggable="true" ondragstart="drag(event)"> {driver.preferred_name} {driver.last_name}</p>
                        {/each}
                    </section>
                    <h2>Passengers</h2>
                    <section id="passengers" ondrop="dropNoCar(event)" ondragover="allowDrop(event)">
                        {#each passengers as passenger}
                            <p class="attendee" id="{passenger.email}" hasCar="false" draggable="true" ondragstart="drag(event)"> {passenger.preferred_name} {passenger.last_name}</p>
                        {/each}
                    </section>
                </section>

                <!-- Right part of page to plan rides -->
                <section id="rides">
                    <section id="carPools" onload="loadRides()">
                        <!-- Create and add new "carPoolBox"s in this section -->
                    </section>
                    <script>
                        // Grab JSON
                        // Create carPools and add to carPools if JSON has data
                        // Remember to remove from list before adding to new carPool
                        // Keep counterCount? and remember to increment
                    </script>
                    <section id="functions">
                        <div id="newCarBox" ondrop="dropNewPool(event)" ondragover="allowDrop(event)">
                            <p class="instructionText">Drop drivers here to create a new carpool</p>
                        </div>    
                        <form on:submit={save}>
                            <button id="saveButton"> Save </button>
                        </form>
                    </section>
                </section>
            </div>
        </main>
    {/if}
</main>