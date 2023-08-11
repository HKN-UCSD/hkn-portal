<script>
    import { onMount } from "svelte";
	import Sidebar from './Sidebar.svelte';
	import Navbar from './Navbar.svelte';
    export let name;
    let apimessage = "Waiting for server...";
	let showSidebar = false;
    onMount(async () => {
        let resp = await fetch("/api/greet").then((res) => res.json());
        console.log(resp);
        apimessage = JSON.stringify(resp);
    });
</script>

<Navbar bind:showSidebar={showSidebar} toggleSidebar={() => showSidebar = !showSidebar} />

{#if showSidebar}
  <Sidebar />
{/if}

<main>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>