
<script>
    import { onMount } from 'svelte';
    import Layout from '../Layout.svelte';
    import {adminStatus} from '../stores.js';
    let onboardingOfficers = [];
    let loading = true;
    let error = null;

    let headers = [
        {"value": 'firstName', "title": "First Name"},
        {"value": 'lastName', "title": "Last Name"},
        {"value": 'position', "title": "Position"},
        {"value": "quarter", "title": "Quarter Inducted"},
        {"value": "newOfficer", "title": "New Officer"}
                  ]

    
    async function getInductees() {
        try {
            let response = await fetch(`/api/officers/`);
            if (response.ok) {
                let onboardings = await response.json();
                return onboardings
            } else {
                throw new Error(response.statusText);
            }
        } catch (err) {
            error = err.message;
        } finally {
            loading = false;
        }
    }

    /* Existing Helper Functions */



    // Fetch data when the component is mounted
    onMount(async () => {
       onboardingOfficers = await getInductees();

    });
</script>


<svelte:head>
    <title> HKN Portal | Onboarding Officers </title>
</svelte:head>
<Layout>
    
    <main>
        {#if $adminStatus === true}
            <section class="top_bar">
            <div style="padding-left:50px">
                <h1 style="margin-left: 15px">Onboarding Officers</h1>
            </div>
            </section>
        {/if}
        <table>
            <tr>
                {#each headers as header}
                    <th>{header["title"]}</th>
                {/each}
            </tr>
            
            {#each onboardingOfficers as onboarding}
                <tr>
                    <td>
                        {onboarding.position}
                    </td>
                </tr>
            {/each}
                

        </table>
    </main>
</Layout>

<style>
    div {
        float:left;
        padding: 10px;
    }
    .top_bar {
        display: flex;
        justify-content: start;
        align-items: start;
        flex-wrap: wrap;
    }
    table {
        /* border: 1px solid grey; */
        border-radius:20px;
        border:solid gray 1px;
        border-collapse: separate;
        height: 60%;
        width: 100%;
        overflow:hidden;
        border-spacing:0;
        float:left;
    }
    th {
        border-collapse: collapse;
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: rgb(44,62,80);
        color: white;
        text-transform: capitalize;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    th:hover {
        cursor: pointer;
        background-color: rgb(24,42,60);
    }
    th:nth-child(1) {
        width: 15%;
    }
    th:nth-child(2) {
        width: 15%;
    }
    th:nth-child(3) {
        width: 25%;
    }
    th:nth-child(4) {
        width: 10%;
    }
    th:nth-child(5) {
        width: 10%;
    }
    th:nth-child(6) {
        width: 10%;
    }
    tr:nth-child(odd) {
        background-color: rgb(240,240,255);
    }
    td {
        padding: 10px;
        overflow: wrap;
    }

    #downloadButton:hover {
        cursor: pointer;
    }

</style>