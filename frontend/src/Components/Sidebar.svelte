<script>

    let logo = "/static/HKN-Logo-New-Blue.png";

    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            return output.is_admin;
        } else {
            throw new Error(response.statusText);
        }
    }
</script>

<style>

  .sidebar {
    width: 224px; 
    height: 100vh;
    background-color: #333;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
  }

  .sidebar img {
    width: 85%;
    margin-top: 30px;
    margin-bottom: 40px;
  }

  .sidebar a {
    color: white;
    text-decoration: none;
    margin: 16px 0;
    padding: 5px 10px;
    display: block;
    width: 100%;
    text-align: center;
    font-size: 21px;
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
{:then adminStatus}
    <!--After getting admin status, load inductee button if allowed to access-->
    <div class="sidebar">
    <img src={logo} alt="HKN logo" />
    <a href="/">Home Page</a>
    <a href="/profile">Profile</a>
    
    {#if adminStatus}
    <a href="/inductees">Inductees</a>
    <a href="/outreach">Outreach</a>
    {/if}

    <a href="/accounts/logout/">Logout</a>
    </div>
{/await}