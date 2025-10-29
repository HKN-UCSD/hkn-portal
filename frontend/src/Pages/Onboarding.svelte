<script>
  import Layout from "../Layout.svelte";
  import { onMount } from "svelte";
  import { adminStatus } from '../stores.js';
  import Navbar from "../Components/Navbar.svelte";
  import SearchBar from "../Components/SearchBar.svelte";
  import Pagination from "../Components/Pagination.svelte";

  let officers = [], filteredData = [], officersDataPerPage = [];
  let searchText = "";
  let sorting_col = "";
  let ascending = true;
  let loading = true;
  let error = null;
  let quarter_options = [];
  let quarter_option = "all";
  let newOfficer_option = "all";
  const newOfficer_options = ["Yes", "No"];

  async function getOfficers() {
    let res = await fetch(`/api/officers/`);
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    return data;
  }

  let headers = [
    {"value": 'preferred_name', "title": 'Name'},
    {"value": 'email', "title": "Email"},
    {"value": 'induction_class', "title": "Class"},
    {"value": 'quarter', "title": "Quarter"},
    {"value": 'newOfficer', "title": "New Officer?"}
  ];

  let classes = [];
  let class_option = "all";

  async function getInductionClasses() {
  const res = await fetch(`/api/inductionclasses/`);
  if (!res.ok) throw new Error(res.statusText);
  const data = await res.json();
  // Sort newest first:
  data.sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
  return data;
}

  // Sorting function
  function sortBy(header) {
    const column = header["value"];
    const isSameColumn = sorting_col == column;
    sorting_col = column;
    ascending = isSameColumn ? !ascending : true;
    filteredData = [...filteredData].sort((a, b) => {
      let aVal = a[column];
      let bVal = b[column];
      // For quarter and newOfficer, handle nested
      if (column === "quarter") {
        aVal = a.onboarding?.quarter ?? "";
        bVal = b.onboarding?.quarter ?? "";
      }
      if (column === "newOfficer") {
        aVal = a.onboarding?.newOfficer ? 1 : 0;
        bVal = b.onboarding?.newOfficer ? 1 : 0;
      }
      let result = 0;
      if (aVal < bVal) result = -1;
      else if (aVal > bVal) result = 1;
      // Tie breaker by name
      else {
        if (a.preferred_name < b.preferred_name) result = -1;
        else if (a.preferred_name > b.preferred_name) result = 1;
      }
      return ascending ? result : -result;
    });
  }

  // Filtering function
  function filter() {
    filteredData = officers.filter(off => {
      // Search text logic
      let passesSearch = true;
      if (searchText) {
        const s = searchText.toLowerCase();
        passesSearch = (
          (off.preferred_name?.toLowerCase() + " " + off.last_name?.toLowerCase()).includes(s)
          || (off.email && off.email.toLowerCase().includes(s))
          || (off.induction_class && off.induction_class.toLowerCase().includes(s))
          || (off.onboarding?.quarter && off.onboarding.quarter.toLowerCase().includes(s))
          || (off.onboarding?.newOfficer ? "yes" : "no").includes(s)
        );
      }
      // Filter by quarter_option and newOfficer_option
      const passesQuarter = (quarter_option === "all" || off.onboarding?.quarter === quarter_option);
      const passesNewOfficer = (newOfficer_option === "all" ||
        (off.onboarding?.newOfficer ? "Yes" : "No") === newOfficer_option);
      const passesClass = class_option === "all" || off.induction_class === class_option;
      return passesSearch && passesQuarter && passesNewOfficer && passesClass;
    });
    // Default sort
    if (sorting_col) {
      sortBy(headers.find(h => h.value === sorting_col));
    }
  }

  // CSV Export
  let csv_data;
  function tableToCSV() {
    let csv = [];
    let row = [];
    headers.forEach(header => {
      row.push(header['title']);
    });
    csv.push(row.join(','));
    filteredData.forEach(off => {
      row = [];
      row.push(off.preferred_name ?? "");
      row.push(off.last_name ?? "");
      row.push(off.email ?? "");
      row.push(off.induction_class ?? "");
      row.push(off.onboarding?.quarter ?? "");
      row.push(off.onboarding?.newOfficer ? "Yes" : "No");
      csv.push(row.join(','));
    });
    csv_data = csv.join('\n');
  }
  function download_table() {
    tableToCSV();
    var textToSave = csv_data;
    var hiddenElement = document.createElement('a');
    hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
    hiddenElement.target = '_blank';
    hiddenElement.download = 'onboarding.csv';
    hiddenElement.click();
  }

  // Reactive filter on searchText, officers, quarter_option, newOfficer_option
  $: {
  searchText, officers, quarter_option, newOfficer_option, class_option;
  if (officers) filter();
}

  onMount(async () => {
  try {
    officers = await getOfficers();
    quarter_options = Array.from(
      new Set(officers.map(o => o.onboarding?.quarter).filter(Boolean))
    );
    classes = await getInductionClasses();
  } catch (e) {
    error = e.message;
  } finally {
    loading = false;
  }
});
</script>

<svelte:head>
  <title>HKN Portal | Onboarding Officers</title>
</svelte:head>

<Layout>
  {#if $adminStatus === true}
    <div class="px-8 py-8 max-w-screen-2xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold">Onboarding Officers</h1>
        <p class="mt-1 text-gray-600">Officer details and onboarding status</p>
      </div>

      {#if loading}
        <p>Loading…</p>
      {:else if error}
        <p class="text-red-600">Error: {error}</p>
      {:else}
        <!-- Controls Section -->
        <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-100">
          <div class="flex flex-col md:flex-row gap-6 items-start md:items-center">
            <!-- Filters -->
            <div class="flex flex-col sm:flex-row gap-3 flex-1">
              <!-- Quarter Filter -->
              <div class="relative">
                <select bind:value={quarter_option}
                        class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all cursor-pointer">
                  <option value="all">All Quarters</option>
                  {#each quarter_options as q}
                    <option value={q}>{q}</option>
                  {/each}
                </select>
              </div>
              <!-- New Officer Filter -->
              <div class="relative">
                <select bind:value={newOfficer_option}
                        class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all cursor-pointer">
                  <option value="all">New Officer?</option>
                  {#each newOfficer_options as opt}
                    <option value={opt}>{opt}</option>
                  {/each}
                </select>
              </div>
              <div class="relative">
                <select bind:value={class_option}
                        class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all cursor-pointer">
                  <option value="all">All Classes</option>
                  {#each classes as c}
                      <option value={c.name}>{c.name}</option>
                  {/each}
                </select>
              </div>
            </div>
            <!-- Search/Download -->
            <div class="flex sm:flex-row flex-col gap-3 w-full md:w-auto">
              <SearchBar bind:searchText
                         class="w-full md:w-64 rounded-lg border-gray-200 focus:border-blue-500" />
              <button on:click={() => download_table()}
                class="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-primary text-white
                       rounded-lg transition-all hover:translate-y-[-1px] shadow-sm items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                Export CSV
              </button>
            </div>
          </div>
        </section>

        <!-- Data Table Section -->
        <div class="flex-1 overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
          <table class="w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                {#each headers as header}
                  <th
                    class="px-6 py-4 text-left text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-100 transition-colors group"
                    on:click={() => sortBy(header)}
                  >
                    <div class="flex items-center gap-2">
                      <span>{header.title}</span>
                      {#if sorting_col === header.value}
                        <span class="text-gray-400">
                          {#if ascending}↑{:else}↓{/if}
                        </span>
                      {:else}
                        <span class="invisible group-hover:visible text-gray-300">↕</span>
                      {/if}
                    </div>
                  </th>
                {/each}
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              {#each officersDataPerPage as off}
                <tr class="hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                    <a href={"/profile/" + off.user_id} class="hover:underline">
                      {off.preferred_name} {off.last_name}
                    </a>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{off.email}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{off.induction_class}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{off.onboarding?.quarter ?? '-'}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{off.onboarding?.newOfficer ? 'Yes' : 'No'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <!-- Pagination -->
        <div class="mt-8">
          <Pagination rows={filteredData} perPage={15} bind:trimmedRows={officersDataPerPage} />
        </div>
      {/if}
    </div>
  {:else if $adminStatus == null}
    <div>Verifying permissions…</div>
  {:else}
    <div class="text-red-600">Unauthorized Access</div>
  {/if}
</Layout>