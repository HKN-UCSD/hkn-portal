<script>
  let logo = "/static/frontend/HKN-Logo-New-Blue.png";
</script>

<style>
  .sidebar {
    width: 200px;
    height: 100vh;
    background-color: #333;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
  }

  .sidebar img {
    width: 150px;
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
  }

  .sidebar a:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

</style>

<div class="sidebar">
  <img src={logo} alt="HKN logo" />
  <a href="/home">Home Page</a>
  <a href="/profile">Profile</a>
  <a href="/accounts/logout/">Logout</a>
</div>