<script>
    import { onMount } from "svelte";
    import { Router, Route } from "svelte-routing"; 
    import Sidebar from "./Components/Sidebar.svelte";
    import Navbar from "./Components/Navbar.svelte"; // Import the responsive navbar component
    import Home from "./Pages/Home.svelte";
    import EventDetail from "./Pages/Events/EventDetail.svelte";
    import EventCreate from "./Pages/Events/EventCreate.svelte";
    import EventRides from "./Pages/Events/EventRides.svelte"
    import Profile from "./Pages/Profile.svelte";
    import Device from 'svelte-device-info';
    //import ProfileEdit from "./Pages/ProfileEdit.svelte";
    import Inductees from "./Pages/Inductees.svelte";
    import Outreach from "./Pages/Outreach.svelte";
    
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
  
    
</script>

{#await getAdminStatus()}
    <div>
        <p>loading...</p>
    </div>
{:then adminStatus}

<Router>
    <div class="main-content">
        <Route component={Home} /> <!--Default route to home-->
        <Route path="/profile/self">
                <Profile id={null}/>
            </Route>
            <Route path="/profile/edit">
                <!--ProfileEdit /-->
            </Route>
        
        {#if adminStatus}
            <Route path="/profile/:id" let:params>
                <Profile id={params.id}/>
            </Route>
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
      
        <Route path="/events/:id" let:params>
            <EventDetail id={params.id}/>
        </Route>
    </div>
</Router>

{/await}

<style>
    :global(:root) {
        --primary-color: #4350AF;
    }

    :global(body) {
        margin: 0px;
        padding: 0px;
    }

</style>


