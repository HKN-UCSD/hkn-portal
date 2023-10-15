<script>
  let logo = "/static/HKN-Logo-New-Blue.png";
</script>

<style>
  .sidebar {
    width: 224px; 
    height: 100%;
    background-color: #333;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
    padding: 15px;
    position: fixed;
    overflow: auto;
    z-index: 100;
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
  <a href="/profile">Profile</a>
  <a href="/accounts/logout/">Logout</a>
</div>