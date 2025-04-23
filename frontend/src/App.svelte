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
    import GachaHome from "./Pages/Collectibles/GachaHome.svelte";
    import Blueprint from "./Pages/Collectibles/Blueprint.svelte";
    import Inventory from "./Pages/Collectibles/Inventory.svelte";
    import Loadout from "./Pages/Collectibles/Loadout.svelte";
    import Catalog from "./Pages/Collectibles/Catalog.svelte";
    import { adminStatus, interviewEligibility } from './stores.js';
</script>


<Router>
    <div class="main-content">
        <Route component={Home} /> <!--Default route to home-->
        <Route path="/profile/self">
            <Profile id={null}/>
        </Route>

        <!-- Collectibles Routes -->
        <Route path="/collectibles/gachahome" component={GachaHome} />
        <Route path="/collectibles/blueprint" component={Blueprint} />
        <Route path="/collectibles/inventory" component={Inventory} />
        <Route path="/collectibles/loadout" component={Loadout} />
        <Route path="/collectibles/catalog" component={Catalog} />

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






