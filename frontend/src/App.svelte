<script>
    import { onMount } from "svelte";
    import { Router, Route } from "svelte-routing";
    import Home from "./Pages/Home.svelte";
    import EventDetail from "./Pages/Events/EventDetail.svelte";
    import EventCreate from "./Pages/Events/EventCreate.svelte";
    import EventRides from "./Pages/Events/EventRides.svelte"
    import Profile from "./Pages/Profile.svelte";
    import ProfileEdit from "./Pages/ProfileEdit.svelte";
    import Inductees from "./Pages/Inductees.svelte";
    import Outreach from "./Pages/Outreach.svelte";
    import House from "./Pages/House.svelte";
    import InterviewSchedule from "./Pages/InterviewSchedule.svelte";
    import EditSchedule from "./Pages/EditSchedule.svelte";
    import { adminStatus, interviewEligibility } from './stores.js';
</script>


<Router>
    <div class="main-content">
        <Route component={Home} /> <!--Default route to home-->
        <Route path="/profile/self">
            <Profile id={null}/>
        </Route>
        <Route path="/profile/edit">
            <ProfileEdit />
        </Route>
        
        {#if $adminStatus !== null}
            <Route path="/profile/:id" let:params>
                <Profile id={params.id}/>
            </Route>
            <Route path="/events/:id" let:params>
                <EventDetail id={params.id}/>
            </Route>
            
            {#if $adminStatus === true}
                <Route path="/inductees" component={Inductees} />
                <Route path="/outreach" component={Outreach} />
                <Route path="/house" component={House}/>
                <Route path="/events/create">
                    <EventCreate />
                </Route>
                <Route path="/events/edit/:id" let:params>
                    <EventCreate idOfEventToEdit={params.id}/>
                </Route>
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



<style>
    :global(:root) {
        --primary-color: #4350AF;
    }

    :global(body) {
        margin: 0px;
        padding: 0px;
    }

</style>


