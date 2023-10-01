<script>
    import Navbar from "./Components/Navbar.svelte";
    import Sidebar from "./Components/Sidebar.svelte";
    import { Router, Route } from "svelte-routing";
    import HomePage from "./Pages/HomePage.svelte";
    import EventsPage from "./Pages/EventsPage.svelte";
    import EventDetailPage from "./Pages/EventDetailPage.svelte";
    import EventHomePage from "./Components/Events/EventHomePage.svelte";
</script>

<Router>
    <!--<Navbar />-->
    <div class="app">
        <Sidebar />
        <div class="main-content">
            <Route path="/home" component={HomePage} />
            <Route path="/profile" component={HomePage} />
            <Route path="/events" component={EventsPage} />
            <Route path="/events/:id" let:params>
                <EventDetailPage id={params.id}/>
            </Route>
            <Route path="/test" component={EventHomePage} />
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
        /*margin-top: 75px;*/
    }

    .main-content {
        flex-grow: 1; /* This allows the main content to take up the remaining space */
        margin-left: 200px;
    }
</style>
