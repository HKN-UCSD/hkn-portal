<script>
    import { Router, Route } from "svelte-routing"; 
    import Sidebar from "./Components/Sidebar.svelte";
    import Home from "./Pages/Home.svelte";
    import Events from "./Pages/Events.svelte";
    import EventDetail from "./Pages/EventDetail.svelte";
    import Profile from "./Pages/Profile.svelte";
    import FormPage from "./Pages/FormPage.svelte";
</script>

<Router>
    <!--<Navbar />-->
    <div class="app">
        <Sidebar />
        <div class="main-content">
            <Route path="/home" component={Home} />
            <Route path="/profile" component={Profile} />
            <Route path="/events" component={Events} />
            <Route path="/events/:id" let:params>
                <EventDetail id={params.id}/>
            </Route>
            <Route path="/events/create">
                <FormPage formURL="/api/interface/create/" />
            </Route>
            <Route path="/events/edit/:id" let:params>
                <FormPage formURL="/api/interface/create/{params.id}/" />
            </Route>
        </div>
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
    :global(.displayhidden) {
        display: none;
    }
    .app {
        display: flex;
    }

    .main-content {
        flex-grow: 1; /* This allows the main content to take up the remaining space */
        margin-left: 200px;
    }
</style>
