<script>

    let logo = "/static/HKN-Logo-New-Blue.png";

    async function getAdminStatus() {
        let response = await fetch(`/api/actions/`);
        if (response.status === 200) {
            let availableActions = await response.json();
            let otherActions = availableActions.other_actions;
            return otherActions;
        } else {
            throw new Error(response.statusText);
        }
    }
</script>

<style>
  .sidebar {
    width: 200px;
    max-width: 20%;
    height: 100%;
    background-color: #333;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
    position: fixed;
    overflow: auto;
    z-index: 100;
  }

  .sidebar img {
    width: 80%;
    margin-bottom: 20px;
  }

  .sidebar a {
    color: white;
    text-decoration: none;
    margin: 10px 0;
    padding: 5px 10px;
    display: block;
    width: 100%;
    text-align: center;
    font-size: max(min(20px, 1.8vw), 10px);
  }

  .sidebar a:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

</style>

<!--While getting admin status, load the other buttons first-->
{#await getAdminStatus()}
    <div class="sidebar">
    <img src={logo} alt="HKN logo" />
    <a href="/">Home Page</a>
    <a href="/profile">Profile</a>
    <a href="/accounts/logout/">Logout</a>
    </div>
{:then otherActions}
    <!--After getting admin status, load inductee button if allowed to access-->
    <div class="sidebar">
    <img src={logo} alt="HKN logo" />
    <a href="/">Home Page</a>
    <a href="/profile">Profile</a>
    
    {#if otherActions.length > 0}
        <a href="/inductees">Inductees</a>
    {/if}

    <a href="/accounts/logout/">Logout</a>
    </div>
{/await}