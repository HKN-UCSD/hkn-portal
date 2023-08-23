<script>
    import { onMount } from "svelte";
    import Navbar from "./Components/Navbar.svelte";
    import Sidebar from "./Components/Sidebar.svelte";
    let apimessage = "Waiting for server...";
	let showSidebar = false;
    onMount(async () => {
        let resp = await fetch("/api/greet").then((res) => res.json());
        console.log(resp);
        apimessage = JSON.stringify(resp);
    });
</script>

<Navbar />
<Sidebar />

<style>

</style>