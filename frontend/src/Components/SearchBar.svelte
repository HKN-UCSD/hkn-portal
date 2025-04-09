<script>
    export let searchText;
    export let className = "";
  </script>
  
  <div class={`flex px-4 py-2 ${className}`}>
    <input 
      type="text" 
      bind:value={searchText} 
      placeholder="Search..."
      class="w-full px-4 py-2 rounded-lg border border-gray-200 text-gray-700 focus:ring-2 focus:ring-secondary focus:border-primary
                                       transition-all"
    />
  </div>
  