<script>
    import { onMount } from "svelte";
    import Navbar from "./Components/Navbar.svelte";
    import Sidebar from "./Components/Sidebar.svelte";
    import { Router, Link, Route } from 'svelte-routing';
    import HomePage from './Pages/HomePage.svelte';
    import ProfilePage from './Pages/ProfilePage.svelte';

    let apimessage = "Waiting for server...";
    
    // Commenting out the onMount logic for now
    onMount(async () => {
        let resp = await fetch("/api/greet").then((res) => res.json());
        console.log(resp);
        apimessage = JSON.stringify(resp);
    });
</script>


<Router>
    <Navbar />
    <div class="app">
        <Sidebar />
        <div class="main-content">
            <Route path="/home" component="{HomePage}" />
            <Route path="/profile" component="{ProfilePage}" />
        </div>
    </div>
</Router>

<style>
  .app {
    display: flex;
}

.main-content {
    flex-grow: 1;  /* This allows the main content to take up the remaining space */
}

</style>