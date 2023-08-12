<script>
  export let showSidebar; // This will receive the value from the parent
  export let toggleSidebar; // This is the function to toggle the sidebar
</script>

<style>
  .navbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding: 10px 20px;
    background-color: #4350AF;
  }

  .navbar img {
    margin-left: 40px;
    height: 40px;
  }

  .navbar a {
    margin: 0 10px;
    color: white;
    text-decoration: none;
  }

  .navbar a:hover {
    text-decoration: underline;
  }

  .navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
  .toggle-button {
    background: "static/frontend/menu_icon.png";
    background-size: contain; /* Adjusts the icon size to fit the button */
    width: 24px; /* Adjust width as necessary */
    height: 24px; /* Adjust height as necessary */
    border: none;
    cursor: pointer;
    color: inherit;
    overflow: hidden; /* Hides any overflowing content */
    padding: 0; /* Remove any default padding */
}



.portal-title {
  font-size: 24px; /* Adjust as necessary */
  font-weight: bold;
  margin-right: 100px; /* Adjust as necessary */
  color: white;
}

</style>

<div class="navbar">
  <div class="navbar-content">
    <button on:click={toggleSidebar} class="toggle-button"></button>
    <span class="portal-title">HKN Portal</span>
  </div>
</div>

