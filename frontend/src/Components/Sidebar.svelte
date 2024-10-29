<script>
    import { adminStatus } from '../stores.js';

    let logo = "/static/HKN-Logo-New-Blue.png";
    let onLogOut = () => {
        sessionStorage.removeItem('adminStatus');
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
    position: fixed;
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

<div class="sidebar">
  <img src={logo} alt="HKN logo" />
  <a href="/">Home Page</a>
  <a href="/profile/self">Profile</a>
  {#if $adminStatus === true}
    <a href="/inductees">Inductees</a>
    <a href="/outreach">Outreach</a>
    <a href="/house">Houses</a>
  {/if}
    <a href="/accounts/logout/" on:click={onLogOut}>Logout</a>
</div>

