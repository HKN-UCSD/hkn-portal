<script>
    import { Router, Route } from "svelte-routing"; 
    import Sidebar from "./Components/Sidebar.svelte";
    import Home from "./Pages/Home.svelte";
    import EventDetail from "./Pages/Events/EventDetail.svelte";
    import EventCreate from "./Pages/Events/EventCreate.svelte";
    import Profile from "./Pages/Profile.svelte";
    import Form from "./Pages/Form.svelte";
</script>

<Router>
    <!--<Navbar />-->
    <div class="app">
        <Sidebar />
        <div class="main-content">
            <Route component={Home} /> <!--Default route to home-->
            <Route path="/profile" component={Profile} />
            <Route path="/events/:id" let:params>
                <EventDetail id={params.id}/>
            </Route>
            <Route path="/events/create">
                <EventCreate />
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
