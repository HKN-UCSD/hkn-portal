<script>
    let logo = "/static/HKN-Logo-New-Blue.png";
  
    let menuItems = [
      { name: "Home", link: "/" },
      { name: "Profile", link: "/profile/self" },
      { name: "Logout", link: "/accounts/logout/" }
    ];
  </script>
  
  <style>
    .navbar {
      width: 100%;
      height: 60px;
      background-color: #333;
      display: flex;
      align-items: center;
      justify-content: space-around;
      top: 0;
      position: fixed;
    }
  
    .navbar img {
      height: 90%; /* Set the height of the image to 80% of the navbar's height */
      object-fit: contain; /* Maintain the image's aspect ratio while fitting it inside the container */
      margin-right: 10px;
    }
  
    .navbar a {
      color: white;
      text-decoration: none;
      font-size: 18px;
      margin: 0 15px;
      display: flex;
      align-items: center;
    }
  
    .navbar a:hover {
      opacity: 0.8;
    }
  </style>
  
  <div class="navbar">
    <img src={logo} alt="HKN logo" />
    {#each menuItems as { name, link }}
      <a href={link}>{name}</a>
    {/each}
  </div>
  