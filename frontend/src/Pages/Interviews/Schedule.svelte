<script>
    import SchedulerLayout from "../../Components/Interviews/SchedulerLayout.svelte";
    import { InterviewCycleNonexistError, AvailabilityNotCreatedError } from "./interviewerrors"
    import * as utils from "./interviewutils"
    import { fetchSelf } from "../../utils"
    import GridSelector from "../../Components/Interviews/GridSelector.svelte";
    import { eachWeekOfInterval } from "date-fns";
    import { each } from "svelte/internal";

    // binaryAvailability should only be assigned by the Schedule component
    // a single time, right here. From hereafter, 
    // only the child GridSelectors may write to this variable. However, reading
    // this value from the GridSelectors is valid and necessary.
    let grids;
    let init = async () => {
        console.log("initializing");

        // Find induction class for the current date
        let inductionClass = await utils.getCurrentInductionClass();
        if (inductionClass === null) {
            console.log("[Schedule.init] No induction class was created for this date.");
            throw new Error("[Schedule.init] No induction class was created for this date.");
        }
        console.log("[Schedule.init] Found induction class.");

        // Obtain interview cycle for the current induction class
        let iCyclePk = inductionClass.interview_cycle;
        if (iCyclePk === null) {
            console.log("[Schedule.init] Interview cycle does not exist")
            throw new InterviewCycleNonexistError("No interview cycle created.");
        } else {
            console.log("iCyclePk is " + iCyclePk);
        }
        console.log("[Schedule.init] Interview cycle for this induction class exists and has been found.")

        // fetch user
        let user = await fetchSelf();

        // fetch availability for this induction class, or make a new one if one doesn't exist
        let availability = await utils.getAvailability(user.user_id, iCyclePk);
        let binaryAvailability = availability.slots === null ? null : utils.base64ToBytes(availability.slots);
        
        let interviewCycle = await utils.getInterviewCycle(iCyclePk);
        if (binaryAvailability === null) {
            console.log("[Schedule.init] Failed to find current availability, attempting to create a new one.");
            binaryAvailability = utils.newAvailability(interviewCycle);
            let postResponse = await utils.postAvailability(user.user_id, binaryAvailability, iCyclePk);
            if (postResponse.status != 200 && postResponse.status != 201) {
                console.log("[Schedule.init] Failed to find current availability and create a new one.");
                throw new AvailabilityNotCreatedError(`No availability created for induction class ${inductionClass.name}`, inductionClass);
            }
            console.log(`Posted new availability for user ${user.user_id}, interview cycle ${iCyclePk}: ${binaryAvailability}`);
        } else {
            console.log(`Found availability: ${binaryAvailability}`);
        }

        // If the fetched availability is invalid, make a new availability.
        if (!utils.slotsBinaryValidForInterviewCycle(binaryAvailability, interviewCycle)) {
            console.log("[Schedule.init] The availability that was retrieved for this user did not encode enough slots for this interview cycle. Creating a new empty one.")
            binaryAvailability = utils.newAvailability(interviewCycle);
        }

        // compute the number of rows (representing a week's availability) to render,
        // and the dimensions for each row.
        let gridWidths = utils.interviewCycleToGridWidths(interviewCycle);
        let gridHeight = utils.slotsInTimeRange(interviewCycle.end_time, interviewCycle.start_time);
        grids = Array(gridWidths.length);

        return {
            "inductionClass": inductionClass,
            "availabilityPk": availability.pk,
            "userId": user.user_id,
            "gridWidths": gridWidths,
            "gridHeight": gridHeight,
            "initialBinary": binaryAvailability
        }
    }

    let p_init = init();

    p_init.catch((reason) => { 
        console.log(reason) 
    });

    let onGridChange = (availabilityPk) => {
        //binaryAvailability = utils.availabilityGridsToBinary(grids);
        let bData = utils.availabilityGridsToBinary(grids);
        let encodedBinary = utils.bytesToBase64(bData);
        utils.putAvailability(availabilityPk, bData);
        console.log(`${bData} was converted to ${encodedBinary} and pushed to availability.`)
    }


</script>


<SchedulerLayout>
    <!-- Title block -->
    <svelte:fragment slot="title-block">
        <h1>Schedule your HKN Induction Interview</h1>
        {#await p_init}
            <h2>Induction Class: </h2>
        {:then {inductionClass} } 
            <h2>Induction Class: { inductionClass.name }</h2>
        {:catch error}
            {#if error instanceof AvailabilityNotCreatedError}
                <h2>Induction Class: {error.inductionClass.name}</h2>
            {:else if error instanceof InterviewCycleNonexistError}
                <h2>Induction Class: None!</h2>
                <p>No induction class has been created for this season yet. Check back soon!</p>
            {/if}
        {/await}
    </svelte:fragment>

    <!-- Availabilities -->
    <svelte:fragment slot="avail-layout">
        {#await p_init}
            <p>Checking availabilities...</p>
        {:then {gridWidths, gridHeight, availabilityPk, initialBinary} } 
            {@const binaryIdxs = utils.prefixSum(gridWidths.map((x) => x * gridHeight))}
            {#each gridWidths as width, i (i)}
                <GridSelector --bordercol="black" bind:dataGrid={grids[i]} gridWidth={width} gridHeight={gridHeight} binaryData={initialBinary} startBit={binaryIdxs[i]} onGridChange={ (_, newGrid) => onGridChange(availabilityPk) }/>
            {/each}
        {:catch error}
            {#if error instanceof AvailabilityNotCreatedError}
                <p>There was an error with creating your availability; there may be an issue with the server right now. Try later or contact the dev team.</p>
            {:else if error instanceof InterviewCycleNonexistError}
                <p>Since your induction class has not been created yet, you cannot schedule your interview.</p>
            {:else}
                <p>Something strange happened that was outside of expectations. Contact the dev team about this issue.</p>
            {/if}
        {/await}
    </svelte:fragment>

    <!-- Controls -->
    <svelte:fragment slot="controls">
        {#await p_init }
            <!-- Other blocks should indicate that the page is loading -->
        {:then {availabilityPk} } 
            <button on:click={ () => onGridChange(availabilityPk) }>Save</button>
        {/await}
    </svelte:fragment>
</SchedulerLayout>

<style>
/*TODO*/
</style>
