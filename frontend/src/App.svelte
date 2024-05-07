<script>
    import { onMount } from "svelte";
    import { Router, Route } from "svelte-routing";
    import Home from "./Pages/Home.svelte";
    import EventDetail from "./Pages/Events/EventDetail.svelte";
    import EventCreate from "./Pages/Events/EventCreate.svelte";
    import EventRides from "./Pages/Events/EventRides.svelte"
    import Profile from "./Pages/Profile.svelte";
    //import ProfileEdit from "./Pages/ProfileEdit.svelte";
    import Inductees from "./Pages/Inductees.svelte";
    import Outreach from "./Pages/Outreach.svelte";
    import { adminStatus } from './stores.js';

    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            let admin = output.is_admin;
            return admin;
        } else {
            throw new Error(response.statusText);
        }
    }

    onMount(async () => {
        let status = sessionStorage.getItem('adminStatus');
        if (sessionStorage.getItem('adminStatus') === null) {
            const status = await getAdminStatus();
            sessionStorage.setItem('adminStatus', status);
            adminStatus.set(status);
        } else {
            adminStatus.set(sessionStorage.getItem('adminStatus'));
        }
        });

</script>


<Router>
    <div class="main-content">
        <Route component={Home} /> <!--Default route to home-->
        <Route path="/profile/self">
                <Profile id={null}/>
            </Route>
            <Route path="/profile/edit">
                <!--ProfileEdit /-->
            </Route>

        {#if $adminStatus !== null}
            <Route path="/profile/:id" let:params>
                <Profile id={params.id}/>
            </Route>
            <Route path="/events/:id" let:params>
                <EventDetail id={params.id}/>
            </Route>
            {#if $adminStatus}
                <Route path="/inductees" component={Inductees} />
                <Route path="/outreach" component={Outreach} />
                <Route path="/events/create">
                    <EventCreate />
                </Route>
                <Route path="/events/edit/:id" let:params>
                    <EventCreate idOfEventToEdit={params.id}/>
                </Route>
                <Route path="/events/rides/:id" let:params>
                    <EventRides id={params.id}/>
                </Route>
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


