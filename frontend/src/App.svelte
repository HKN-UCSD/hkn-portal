<script>
    import { onMount } from "svelte";
    import { Router, Route } from "svelte-routing"; 
    import Sidebar from "./Components/Sidebar.svelte";
    import Navbar from "./Components/Navbar.svelte"; // Import the responsive navbar component
    import Home from "./Pages/Home.svelte";
    import EventDetail from "./Pages/Events/EventDetail.svelte";
    import EventCreate from "./Pages/Events/EventCreate.svelte";
    import Profile from "./Pages/Profile.svelte";
    
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
  

    let isSmallScreen = false;

    // Check window size on mount and set the isSmallScreen variable
    onMount(() => {
        isSmallScreen = window.innerWidth <= 768;
    });

    // Add a resize event listener to dynamically update isSmallScreen variable
    window.addEventListener("resize", () => {
        isSmallScreen = window.innerWidth <= 768;
    });
</script>

{#await getAdminStatus()}
    <div>
        <p>loading...</p>
    </div>
{:then adminStatus}

<Router>
    <div class="app">
        {#if isSmallScreen}
            <Navbar /> <!-- Show the responsive navbar on small screens -->
        {:else}
            <Sidebar /> <!-- Show the sidebar on larger screens -->
        {/if}
        <div class="main-content">
            <Route component={Home} /> <!--Default route to home-->
            <Route path="/profile" component={Profile} />
            
            {#if adminStatus}
                <Route path="/inductees" component={Inductees} />
                <Route path="/outreach" component={Outreach} />
                
                <Route path="/events/create">
                    <EventCreate />
                </Route>
                <Route path="/events/edit/:id" let:params>
                    <EventCreate idOfEventToEdit={params.id}/>
                </Route>
            {/if}

            <Route path="/events/:id" let:params>
                <EventDetail id={params.id}/>
            </Route>
        </div>
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
    :global(.displayhidden) {
        display: none;
    }
    .app {
        display: flex;
        flex-direction: column;
    }

    .main-content {
        flex-grow: 1; /* This allows the main content to take up the remaining space */
        margin-left: 0; /* Remove the left margin for main content */
        margin-top: 60px;
    }

    /* Media query for larger screens */
    @media (min-width: 769px) {
        .app {
            flex-direction: row;
        }

        .main-content {
            margin-left: 254px;
        }
    }
</style>