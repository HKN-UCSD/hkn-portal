<script>
    import { onMount } from "svelte";
    import { Router, Route } from "svelte-routing";
    import Home from "./Pages/Home.svelte";
    import EventRides from "./Pages/EventRides.svelte"
    import Members from "./Pages/Members.svelte";
    import Events from "./Pages/Events.svelte";
    import Profile from "./Pages/Profile.svelte";
    import Inductees from "./Pages/Inductees.svelte";
    import Outreach from "./Pages/Outreach.svelte";
    import House from "./Pages/House.svelte";
    import InterviewSchedule from "./Pages/InterviewSchedule.svelte";
    import EditSchedule from "./Pages/EditSchedule.svelte";
    import { adminStatus, interviewEligibility, refreshInterviewEligibility, } from './stores.js';
    import { toastMessage, showToast } from './Components/Events/toaststore';
    


    onMount(() => {
        refreshInterviewEligibility();
    }); 
</script>


<Router>
    <div class="main-content">
        <Route component={Home} /> <!--Default route to home-->
        <Route path="/profile/self">
            <Profile id={null}/>
        </Route>

        {#if $adminStatus !== null}
            <Route path="/profile/:id" let:params>
                <Profile id={params.id}/>
            </Route>
            <Route path = "/events" component ={Events}/>
            <Route path="/members" component={Members} />
            {#if $adminStatus === true}
                <Route path="/inductees" component={Inductees} />
                <Route path="/outreach" component={Outreach} />
                <Route path="/house" component={House}/>
                <Route path="/events/rides/:id" let:params>
                    <EventRides id={params.id}/>
                </Route>
                <Route path="/schedule" component={InterviewSchedule} />
            {/if}
            {#if $adminStatus === true || $interviewEligibility === true}
                <Route path="/editschedule" component={EditSchedule} />
            {/if}
        {/if}
    </div>
</Router>

{#if $showToast}
    <div class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-600 text-white px-4 py-2 rounded shadow-lg z-50">
        {$toastMessage}
    </div>
{/if}






