<script>
    import { getEvent } from "../Components/Events/eventstore";
    import { populateFormToUpdateRides } from "../Components/Events/eventutils"
    import { onMount, tick } from "svelte";
    import { readable, writable } from "svelte/store";
    import Layout from "../Layout.svelte";
    export let id;

    // Add a store to track number of carpools
    const carpoolCount = writable(0);

    // Update carpool count when carpools are added or removed
    function updateCarpoolCount() {
        const container = document.getElementById("carPools");
        if (container) {
            carpoolCount.set(container.children.length);
        }
    }

    // Add observer to watch for changes in carPools container
    onMount(() => {
        const observer = new MutationObserver(updateCarpoolCount);
        const container = document.getElementById("carPools");
        if (container) {
            observer.observe(container, { childList: true });
        }
        return () => observer.disconnect();
    });

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

    // Helper function to load and populate carpools from event data
    async function loadCarpools(eventRides) {
        // Define parseEmail function if not in scope
        function parseEmail(attendee) {
            return attendee.split("(")[1].split(")")[0];
        }

        // Clear existing carpools first
        const existingContainer = document.getElementById("carPools");
        if (existingContainer) {
            // Move all drivers and passengers back to their lists before clearing
            const drivers = existingContainer.querySelectorAll(".driverBox .attendee");
            const passengers = existingContainer.querySelectorAll(".passengerBox .attendee");
            
            const driversSection = document.getElementById("drivers");
            const passengersSection = document.getElementById("passengers");
            
            if (driversSection && passengersSection) {
                drivers.forEach(driver => driversSection.appendChild(driver));
                passengers.forEach(passenger => passengersSection.appendChild(passenger));
            }
            
            existingContainer.innerHTML = '';
        }

        // If there are no rides to load, just update the count and return
        if (!eventRides || Object.keys(eventRides).length === 0) {
            updateCarpoolCount();
            return [];
        }

        let counter = 1;
        let unRSVPs = [];
        let carPoolsContainer = existingContainer;
        
        // Create container if it doesn't exist
        if (!carPoolsContainer) {
            carPoolsContainer = document.createElement("section");
            carPoolsContainer.setAttribute("id", "carPools");
            carPoolsContainer.setAttribute("class", "bg-white rounded-xl shadow-md p-6 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-4");
            
            // Replace the empty state message with the carPools container
            const emptyState = document.querySelector(".lg\\:w-2\\/3 > div:last-child");
            if (emptyState) {
                emptyState.replaceWith(carPoolsContainer);
            } else {
                // If we can't find the empty state, find the parent container
                const parentContainer = document.querySelector(".lg\\:w-2\\/3");
                if (parentContainer) {
                    parentContainer.appendChild(carPoolsContainer);
                } else {
                    console.error("Could not find parent container for carpools");
                    return [];
                }
            }
        }
        
        for (const key in eventRides) {
            // Create new 'div' named 'carPool{counter}'
            let newCarPool = document.createElement("div");
            newCarPool.setAttribute("id", `carPool${counter}`);
            newCarPool.setAttribute("class", "carPool bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 p-4 flex flex-col");

            // Create delete button for 'div'
            let deleteButton = document.createElement("button");
            deleteButton.addEventListener("click", () => deleteCarPool(newCarPool));
            deleteButton.setAttribute("id", "deleteButton");
            deleteButton.setAttribute("class", "text-gray-500 hover:text-red-500 transition-colors duration-200 text-xl font-medium px-2 rounded-full hover:bg-red-100");
            deleteButton.innerHTML = "×";

            // Create a header flex container for driver heading and delete button
            let headerContainer = document.createElement("div");
            headerContainer.setAttribute("class", "flex justify-between items-center mb-2");

            // Create driver section heading
            let driverHeading = document.createElement("p");
            driverHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary");
            driverHeading.innerHTML = "Driver";

            // Add driver heading and delete button to the header container
            headerContainer.appendChild(driverHeading);
            headerContainer.appendChild(deleteButton);

            // Create box to drag and drop drivers into
            let driverBox = document.createElement("div");
            driverBox.setAttribute("id", `driverBox${counter}`);
            driverBox.setAttribute("class", "driverBox min-h-[60px] bg-gray-50 rounded-md p-2 mb-4 border-2 border-dashed border-gray-200 overflow-x-auto");
            driverBox.addEventListener("drop", (e) => addDriver(e, driverBox));
            driverBox.addEventListener("dragover", allowDrop);

            // Create passenger section heading
            let passengerHeading = document.createElement("p");
            passengerHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary mb-2");
            passengerHeading.innerHTML = "Passengers";

            // Create box to drag and drop passengers into
            let passengerBox = document.createElement("div");
            passengerBox.setAttribute("id", `passengerBox${counter}`);
            passengerBox.setAttribute("class", "passengerBox bg-gray-50 rounded-md p-2 border-2 border-dashed border-gray-200 flex-1 flex flex-col overflow-x-auto");

            // Create a 'div' to indicate to user where to drop passengers
            let addPassengerSign = document.createElement("div");
            addPassengerSign.addEventListener("drop", (e) => addPassenger(e, passengerBox));
            addPassengerSign.setAttribute("class", "addPassengerSign flex items-center justify-center flex-1");
            addPassengerSign.addEventListener("dragover", allowDrop);

            // Create the text instructions for users
            let addPassengerText = document.createElement("p");
            addPassengerText.setAttribute("class", "instructionText text-gray-400 text-center");
            addPassengerText.innerHTML = "Drop passengers here";

            // Construct carpool
            newCarPool.append(
                headerContainer,
                driverBox,
                passengerHeading,
                passengerBox,
            );
            
            passengerBox.appendChild(addPassengerSign);
            addPassengerSign.appendChild(addPassengerText);

            // Insert driver and passengers
            if (eventRides[key]["driver"]) {
                try {
                    const driverEmail = parseEmail(eventRides[key]["driver"]);
                    const driver = document.getElementById(driverEmail);
                    if (driver) {
                        driverBox.appendChild(driver);
                    } else {
                        unRSVPs.push(eventRides[key]["driver"]);
                    }
                }
                catch {
                    unRSVPs.push(eventRides[key]["driver"]);
                }
            }

            if (eventRides[key]["passengers"] && Array.isArray(eventRides[key]["passengers"])) {
                for (const attendee of eventRides[key]["passengers"]) {
                    try {
                        const passengerEmail = parseEmail(attendee);
                        const passenger = document.getElementById(passengerEmail);
                        if (passenger) {
                            passengerBox.insertBefore(passenger, passengerBox.lastChild);
                        } else {
                            unRSVPs.push(attendee);
                        }
                    }
                    catch {
                        unRSVPs.push(attendee);
                    }
                }
            }

            // Add carpool to container
            carPoolsContainer.appendChild(newCarPool);
            counter++;
        }

        updateCarpoolCount();
        return unRSVPs;
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
            const updatedEvent = await response.json();
            const unRSVPs = await loadCarpools(updatedEvent.rides);
            
            if (unRSVPs.length > 0) {
                let alertMessage = 'The following attendees have un-RSVP\'d: \n';
                for (const attendee of unRSVPs) {
                    alertMessage += attendee + '\n';
                }
                alertMessage += 'They will automatically be removed from their assigned rides';
                alert(alertMessage);
                // Save again to remove un-RSVP'd attendees
                let saveEvent = new Event('submit', {isTrusted: true, cancelable: true});
                save(saveEvent);
            } else {
                alert("Saved");
            }
        } else {
            alert(`Unable to save. Response status ${response.status}`);
        }
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
            return attendee.split("(")[1].split(")")[0];
        }

        onMount(async () => {
            const event = await getEvent(id);
            const [attendees, outreachStudents, users] = await Promise.all([
                getAttendees(event),
                getOutreachStudents(),
                getUsers(),
            ]);

            let unRSVPs = [];

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
            if (event.rides && Object.keys(event.rides).length > 0) {
                // Set carpool count to trigger the container creation in the UI
                carpoolCount.set(Object.keys(event.rides).length);
                
                // Wait for the next tick to ensure the container is created in the DOM
                await tick();
                
                // Get or create the container
                let carPoolsContainer = document.getElementById("carPools");
                if (!carPoolsContainer) {
                    carPoolsContainer = document.createElement("section");
                    carPoolsContainer.setAttribute("id", "carPools");
                    carPoolsContainer.setAttribute("class", "bg-white rounded-xl shadow-md p-6 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-4");
                    
                    // Replace the empty state message with the carPools container
                    const emptyState = document.querySelector(".lg\\:w-2\\/3 > div:last-child");
                    if (emptyState) {
                        emptyState.replaceWith(carPoolsContainer);
                    } else {
                        // If we can't find the empty state, find the parent container
                        const parentContainer = document.querySelector(".lg\\:w-2\\/3");
                        if (parentContainer) {
                            parentContainer.appendChild(carPoolsContainer);
                        } else {
                            console.error("Could not find parent container for carpools");
                            return;
                        }
                    }
                }
                
                let counter = 1;
                let unRSVPs = [];
                
                for (const key in event.rides) {
                    // Create new 'div' named 'carPool{counter}'
                    let newCarPool = document.createElement("div");
                    newCarPool.setAttribute("id", `carPool${counter}`);
                    newCarPool.setAttribute("class", "carPool bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 p-4 flex flex-col");

                    // Create delete button for 'div'
                    let deleteButton = document.createElement("button");
                    deleteButton.addEventListener("click", () => deleteCarPool(newCarPool));
                    deleteButton.setAttribute("id", "deleteButton");
                    deleteButton.setAttribute("class", "text-gray-500 hover:text-red-500 transition-colors duration-200 text-xl font-medium px-2 rounded-full hover:bg-red-100");
                    deleteButton.innerHTML = "×";

                    // Create a header flex container for driver heading and delete button
                    let headerContainer = document.createElement("div");
                    headerContainer.setAttribute("class", "flex justify-between items-center mb-2");

                    // Create driver section heading
                    let driverHeading = document.createElement("p");
                    driverHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary");
                    driverHeading.innerHTML = "Driver";

                    // Add driver heading and delete button to the header container
                    headerContainer.appendChild(driverHeading);
                    headerContainer.appendChild(deleteButton);

                    // Create box to drag and drop drivers into
                    let driverBox = document.createElement("div");
                    driverBox.setAttribute("id", `driverBox${counter}`);
                    driverBox.setAttribute("class", "driverBox min-h-[60px] bg-gray-50 rounded-md p-2 mb-4 border-2 border-dashed border-gray-200 overflow-x-auto");
                    driverBox.addEventListener("drop", (e) => addDriver(e, driverBox));
                    driverBox.addEventListener("dragover", allowDrop);

                    // Create passenger section heading
                    let passengerHeading = document.createElement("p");
                    passengerHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary mb-2");
                    passengerHeading.innerHTML = "Passengers";

                    // Create box to drag and drop passengers into
                    let passengerBox = document.createElement("div");
                    passengerBox.setAttribute("id", `passengerBox${counter}`);
                    passengerBox.setAttribute("class", "passengerBox bg-gray-50 rounded-md p-2 border-2 border-dashed border-gray-200 flex-1 flex flex-col overflow-x-auto");

                    // Create a 'div' to indicate to user where to drop passengers
                    let addPassengerSign = document.createElement("div");
                    addPassengerSign.addEventListener("drop", (e) => addPassenger(e, passengerBox));
                    addPassengerSign.setAttribute("class", "addPassengerSign flex items-center justify-center flex-1");
                    addPassengerSign.addEventListener("dragover", allowDrop);

                    // Create the text instructions for users
                    let addPassengerText = document.createElement("p");
                    addPassengerText.setAttribute("class", "instructionText text-gray-400 text-center");
                    addPassengerText.innerHTML = "Drop passengers here";

                    // Construct carpool
                    newCarPool.append(
                        headerContainer,
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
                            if (driver) {
                                driverBox.appendChild(driver);
                            } else {
                                unRSVPs.push(event.rides[key]["driver"]);
                            }
                        }
                        catch {
                            unRSVPs.push(event.rides[key]["driver"]);
                        }
                    }

                    if (event.rides[key]["passengers"] && Array.isArray(event.rides[key]["passengers"])) {
                        for (const attendee of event.rides[key]["passengers"]) {
                            try {
                                const passengerEmail = parseEmail(attendee);
                                const passenger = document.getElementById(passengerEmail);
                                if (passenger) {
                                    passengerBox.insertBefore(passenger, passengerBox.lastChild);
                                } else {
                                    unRSVPs.push(attendee);
                                }
                            }
                            catch {
                                unRSVPs.push(attendee);
                            }
                        }
                    }

                    // Add carpool to container
                    carPoolsContainer.appendChild(newCarPool);
                    counter++;
                }

                // Update the count after all carpools are added
                updateCarpoolCount();

                if (unRSVPs.length != 0) {
                    let alertMessage = 'The following attendees have un-RSVP\'d: \n'
                    for (const attendee of unRSVPs) {
                        alertMessage += attendee + '\n';
                    }
                    alertMessage += 'They will automatically be removed from their assigned rides';
                    alert(alertMessage);
                    let saveEvent = new Event('submit', {isTrusted: true, cancelable: true})
                    save(saveEvent);
                }
            }
        });
    });

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

        let element_id = event.dataTransfer.getData("id");
        let element = document.getElementById(element_id);

        // Check if attendee is a driver
        if (element.getAttribute("hasCar") == "true") {
            // First, update the carpoolCount to ensure the container is shown
            carpoolCount.update(count => Math.max(count + 1, 1));
            
            // Wait for the next tick to ensure the container is in the DOM
            setTimeout(() => {
                // Get the existing carPools container from the template
                let carPoolsContainer = document.getElementById("carPools");
                
                // If the container doesn't exist (something went wrong with reactive rendering)
                if (!carPoolsContainer) {
                    console.warn("Expected carPools container to exist due to carpoolCount > 0");
                    // Find the parent container
                    const parentContainer = document.querySelector(".lg\\:w-2\\/3");
                    if (parentContainer) {
                        // Remove any existing empty state
                        const existingEmptyState = parentContainer.querySelector("div.flex.items-center.justify-center");
                        if (existingEmptyState) {
                            existingEmptyState.remove();
                        }
                        
                        // Create the container as a fallback
                        carPoolsContainer = document.createElement("section");
                        carPoolsContainer.setAttribute("id", "carPools");
                        carPoolsContainer.setAttribute("class", "bg-white rounded-xl shadow-md p-6 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-4");
                        parentContainer.appendChild(carPoolsContainer);
                    }
                }
                
                // If we now have a valid container, create the carpool
                if (carPoolsContainer) {
                    // Create new carpool and add it to the container
                    createCarPool(element, carPoolsContainer);
                    
                    // Update the carpool count to ensure the UI state is correct
                    updateCarpoolCount();
                } else {
                    // If we still don't have a container, just put the driver back
                    document.getElementById("drivers").appendChild(element);
                    console.error("Could not find or create carPools container");
                }
            }, 0);
        } else {
            document.getElementById("passengers").appendChild(element);
        }
    }

    // Helper function to create a new carpool
    function createCarPool(driver, container) {
        // use a counter so created id's don't repeat
        let counter = container.children.length + 1;

        // Create new 'div' named 'carPool{counter}'
        let newCarPool = document.createElement("div");
        newCarPool.setAttribute("id", `carPool${counter}`);
        newCarPool.setAttribute("class", "carPool bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 p-4 flex flex-col");

        // Create delete button for 'div'
        let deleteButton = document.createElement("button");
        deleteButton.addEventListener("click", () => deleteCarPool(newCarPool));
        deleteButton.setAttribute("id", "deleteButton");
        deleteButton.setAttribute("class", "text-gray-500 hover:text-red-500 transition-colors duration-200 text-xl font-medium px-2 rounded-full hover:bg-red-100");
        deleteButton.innerHTML = "×";

        // Create a header flex container for driver heading and delete button
        let headerContainer = document.createElement("div");
        headerContainer.setAttribute("class", "flex justify-between items-center mb-2");

        // Create driver section heading
        let driverHeading = document.createElement("p");
        driverHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary");
        driverHeading.innerHTML = "Driver";

        // Add driver heading and delete button to the header container
        headerContainer.appendChild(driverHeading);
        headerContainer.appendChild(deleteButton);

        // Create box to drag and drop drivers into
        let driverBox = document.createElement("div");
        driverBox.setAttribute("id", `driverBox${counter}`);
        driverBox.setAttribute("class", "driverBox min-h-[60px] bg-gray-50 rounded-md p-2 mb-4 border-2 border-dashed border-gray-200 overflow-x-auto");
        driverBox.addEventListener("drop", (e) => addDriver(e, driverBox));
        driverBox.addEventListener("dragover", allowDrop);

        // Create passenger section heading
        let passengerHeading = document.createElement("p");
        passengerHeading.setAttribute("class", "poolSectionHeading text-lg font-semibold text-primary mb-2");
        passengerHeading.innerHTML = "Passengers";

        // Create box to drag and drop passengers into
        let passengerBox = document.createElement("div");
        passengerBox.setAttribute("id", `passengerBox${counter}`);
        passengerBox.setAttribute("class", "passengerBox bg-gray-50 rounded-md p-2 border-2 border-dashed border-gray-200 flex-1 flex flex-col overflow-x-auto");

        // Create a 'div' to indicate to user where to drop passengers
        let addPassengerSign = document.createElement("div");
        addPassengerSign.addEventListener("drop", (e) => addPassenger(e, passengerBox));
        addPassengerSign.setAttribute("class", "addPassengerSign flex items-center justify-center flex-1");
        addPassengerSign.addEventListener("dragover", allowDrop);

        // Create the text instructions for users
        let addPassengerText = document.createElement("p");
        addPassengerText.setAttribute("class", "instructionText text-gray-400 text-center");
        addPassengerText.innerHTML = "Drop passengers here";

        // Add all created elements to carpool
        newCarPool.append(
            headerContainer,
            driverBox,
            passengerHeading,
            passengerBox,
        );

        // Add dragged and dropped user as the driver
        driverBox.appendChild(driver);

        passengerBox.appendChild(addPassengerSign);
        addPassengerSign.appendChild(addPassengerText);

        container.appendChild(newCarPool);
        updateCarpoolCount(); // Update the count after adding the carpool
    }

    // Add a driver to the carPool's driverBox
    // Parameter: event, driverBox (container to add element to)
    // Output: Add dragged element to driverBox if there isn't already a driver
    //         or swap with existing driver if driverBox already has a driver
    function addDriver(event, driverBox) {
        event.preventDefault();
        let element_id = event.dataTransfer.getData("id");
        let element = document.getElementById(element_id);
        
        if (element.getAttribute("hasCar") == "true") {
            // Check if there's already a driver in the box
            if (driverBox.children.length > 0 && driverBox.firstChild.classList.contains("attendee")) {
                // Get the existing driver
                const existingDriver = driverBox.firstChild;
                
                // Check if the dragged driver is coming from another carpool
                const sourceDriverBox = element.parentElement;
                const isFromCarpool = sourceDriverBox && sourceDriverBox.classList.contains("driverBox");
                
                // If driver is coming from another carpool, swap the drivers
                if (isFromCarpool) {
                    // Put existing driver in the source carpool
                    sourceDriverBox.appendChild(existingDriver);
                    // Put new driver in this carpool
                    driverBox.appendChild(element);
                } else {
                    // Driver is coming from drivers list, move existing driver back to list
                    const driversSection = document.getElementById("drivers");
                    driversSection.appendChild(existingDriver);
                    // Add the new driver to the box
                    driverBox.appendChild(element);
                }
            } 
            // If box is empty, just add the driver
            else if (driverBox.children.length < 1) {
                driverBox.appendChild(element);
            }
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
        // Get the driver and passenger elements before removing
        const driverBox = carPool.querySelector(".driverBox");
        const passengerBox = carPool.querySelector(".passengerBox");
        
        // Move driver back to drivers section if exists
        if (driverBox && driverBox.firstChild && driverBox.firstChild.classList.contains("attendee")) {
            document.getElementById("drivers").appendChild(driverBox.firstChild);
        }
        
        // Move all passengers back to passengers section
        if (passengerBox) {
            const passengers = passengerBox.querySelectorAll(".attendee");
            const passengersSection = document.getElementById("passengers");
            passengers.forEach(passenger => {
                passengersSection.appendChild(passenger);
            });
        }

        // Remove the carpool and all its event listeners
        carPool.remove();
        updateCarpoolCount();
    }
</script>

<svelte:head>
    <title> HKN Portal | Ride Assignment</title>
</svelte:head>
<Layout>
    <main class="min-h-screen">
        {#if $loading}
            <div class="flex items-center justify-center min-h-screen">
                <p class="text-lg text-gray-600">Loading...</p>
            </div>
        {:else}
            <!-- Header Section -->
            <div class="px-8 py-4 mb-6">
                <div class="max-w-7xl mx-auto flex justify-between items-center">
                    <h1 class="text-3xl font-bold text-gray-900 transition-transform duration-300 hover:scale-110">Ride Assignment</h1>
                    <a id="eventLink" href="/events/{id}" 
                        class="py-2 px-4 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105 shadow-md bg-primary">
                        Back to Event
                    </a>
                </div>
            </div>

            <!-- Main Content -->
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-10">
                <div class="flex flex-col lg:flex-row gap-6">
                    <!-- Left Column - Attendees -->
                    <section id="attendees" class="lg:w-1/3 relative bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-300 h-[calc(100vh-12rem)] flex flex-col overflow-y-auto">
                        <div class="flex flex-col h-full">
                            <!-- Drivers Section -->
                            <div class="flex-1 min-h-fit">
                                <h2 class="text-xl font-bold text-primary mb-4 flex items-center">
                                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                    </svg>
                                    Drivers
                                </h2>
                                <section id="drivers" 
                                    class="bg-white rounded-lg border border-gray-200 p-3 min-h-[120px]" 
                                    on:drop={dropCar} 
                                    on:dragover={allowDrop}>
                                    {#each drivers as driver}
                                        <p class="attendee mb-2 last:mb-0 rounded-lg bg-white shadow-sm hover:shadow-md border border-gray-100 cursor-grabbing transition-all duration-200 flex items-center px-4 py-3 overflow-x-auto" 
                                            id="{driver.email}" 
                                            hasCar="true" 
                                            draggable="true" 
                                            on:dragstart={drag}>
                                            {driver.preferred_name} {driver.last_name}
                                        </p>
                                    {/each}
                                </section>
                            </div>

                            <!-- Passengers Section -->
                            <div class="flex-1 min-h-fit mt-6">
                                <h2 class="text-xl font-bold text-primary mb-4 flex items-center">
                                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                                    </svg>
                                    Passengers
                                </h2>
                                <section id="passengers" 
                                    class="bg-white rounded-lg border border-gray-200 p-3 min-h-[120px]" 
                                    on:drop={dropNoCar} 
                                    on:dragover={allowDrop}>
                                    {#each passengers as passenger}
                                        <p class="attendee mb-2 last:mb-0 rounded-lg bg-white shadow-sm hover:shadow-md border border-gray-100 cursor-grabbing transition-all duration-200 flex items-center px-4 py-3 overflow-x-auto" 
                                            id="{passenger.email}" 
                                            hasCar="false" 
                                            draggable="true" 
                                            on:dragstart={drag}>
                                            {passenger.preferred_name} {passenger.last_name}
                                        </p>
                                    {/each}
                                </section>
                            </div>
                        </div>
                    </section>

                    <!-- Right Column - Carpools -->
                    <section class="lg:w-2/3 flex flex-col h-[calc(100vh-12rem)]">
                        <!-- Controls Section -->
                        <div class="relative bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-300 mb-6 flex-shrink-0">
                            <div class="flex items-center justify-between">
                                <div id="newCarBox" 
                                    class="flex-1 mr-4 rounded-lg bg-primary bg-opacity-90 shadow-md hover:shadow-lg transition-all duration-200 p-4 cursor-pointer" 
                                    on:drop={dropNewPool} 
                                    on:dragover={allowDrop}>
                                    <p class="instructionText text-white text-center font-medium flex items-center justify-center">
                                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                        </svg>
                                        Drop drivers here to create a new carpool
                                    </p>
                                </div>
                                <form on:submit={save} class="flex-shrink-0">
                                    <button id="saveButton" 
                                        class="py-3 px-6 rounded-lg font-semibold text-white transition-all duration-300 transform hover:scale-105 shadow-lg bg-primary flex items-center">
                                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
                                        </svg>
                                        Save
                                    </button>
                                </form>
                            </div>
                        </div>

                        <!-- Carpools Section -->
                        {#if $carpoolCount > 0}
                            <section id="carPools" class="relative bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-300 flex-1 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-4 min-h-0">
                                <!-- Carpools will be dynamically added here -->
                            </section>
                        {:else}
                            <div class="relative bg-gray-50 p-8 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-300 flex-1 flex items-center justify-center overflow-y-auto min-h-0">
                                <p class="text-gray-500 text-center">
                                    <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
                                    </svg>
                                    No carpools created yet.<br>
                                    <span class="text-sm">Drag a driver to the box above to create one.</span>
                                </p>
                            </div>
                        {/if}
                    </section>
                </div>
            </div>
        {/if}
    </main>
</Layout>