<script>
    import Navbar from "../Components/Navbar.svelte";
    import Layout from "../Layout.svelte";
    import Pagination from "../Components/Pagination.svelte";
    import { onMount } from "svelte";
    import { adminStatus } from '../stores.js';
    import SearchBar from "../Components/SearchBar.svelte";


    async function getMajors() {
        return await (await(fetch(`api/majors/`))).json()
    }

    let majors = [];
    let years = [];

    async function getInductees() {
        let response = await fetch(`/api/inductees/`);
        if (response.status === 200) {
            let possible_majors = (await getMajors()).map(major => major.name)
            let users = await response.json();
            users.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            for (let i = 0; i < users.length; i++) {
                if (!majors.includes(users[i].major) && possible_majors.includes(users[i].major)) {
                    majors.push(users[i].major);
                }
                if (!years.includes(users[i].grad_year)) {
                    years.push(users[i].grad_year);
                }
            }
            majors.sort();
            years.sort();
            majors.push('Other');
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getInductionClasses() {
        let response = await fetch(`/api/inductionclasses/`);
        if (response.status === 200) {
            let output = await response.json();
            return output;
        } else {
            throw new Error(response.statusText);
        }
    }

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'major', "title": 'Major'},
        {"value": 'grad_year', "title": 'Year'},
        {"value": 'induction_class', "title": 'Class'},
        {"value": 'professional_points', "title": 'P'},
        {"value": 'social_points', "title": 'S'},
        {"value": 'technical_points', "title": 'T'},
        {"value": 'outreach_points', "title": 'O'},
        {"value": 'mentorship_points', "title": 'M'},
        {"value": 'general_points', "title": 'G'},
        {"value": 'total_points', "title": 'Total'}
    ]

    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;

        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            inducteesData = inducteesData.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            inducteesData = inducteesData.sort((first, second) => {
                if (first[sorting_col] > second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        }
    }


    let sorting_col = "N/A";
    let ascending = true;

    let major_option;
    let year_option;
    let class_option;
    let searchText = "";

    let csv_data;

    /*
    * Convert the inducteesData data to CSV format

    */
    function tableToCSV() {
        let csv = [];
        let row = [];
        // Add the headers to the CSV
        headers.forEach(header => {
            row.push(header['title']);
        });
        csv.push(row.join(','));
        // Add the data to the CSV
        inducteesData.forEach(inducteeData => {
            row = [];
            row.push(inducteeData.preferred_name);
            row.push(inducteeData.last_name);
            row.push(inducteeData.email);
            row.push(inducteeData.major);
            row.push(inducteeData.grad_year);
            row.push(inducteeData.induction_class);
            row.push(inducteeData.professional_points);
            row.push(inducteeData.social_points);
            row.push(inducteeData.technical_points);
            row.push(inducteeData.outreach_points);
            row.push(inducteeData.mentorship_points);
            row.push(inducteeData.general_points);
            row.push(inducteeData.total_points);
            csv.push(row.join(','));
        });
        csv_data = csv;
        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }


    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'inductees.csv';
        hiddenElement.click();
    }
    let filteredData;

    function filter() {
        filteredData = inducteesData.filter(inducteeData => {
            return (major_option == "all" || inducteeData.major == major_option
                        || (major_option == "Other" && !majors.includes(inducteeData.major)))
                    && (year_option == "all" || inducteeData.grad_year == parseInt(year_option))
                    && (class_option == "all" || inducteeData.induction_class == class_option)
                    && (searchText == "" || (inducteeData.preferred_name.toLowerCase() + " " + inducteeData.last_name.toLowerCase()).includes(searchText.toLowerCase())
                        || inducteeData.email.toLowerCase().includes(searchText.toLowerCase()));
        });
    }

    let inducteesData, classes;

    let inducteeDataPerPage = [];

    let showLegend = false;

    onMount(async () => {
        inducteesData = await getInductees();
        classes = await getInductionClasses();
        console.log(inducteesData)
    });
    // filter the data when the inducteesData and classes are loaded if any of the options changes
    $: {
        major_option, year_option, class_option, searchText;
        if (inducteesData && classes) filter();
        }
</script>

<svelte:head>
    <title> HKN Portal | Inductees </title>
</svelte:head>

<Layout>
    {#if $adminStatus === true}
      <div class="px-8 py-8 max-w-screen-2xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Inductee Management</h1>
          <p class="mt-2 text-gray-600">View and manage inductee records</p>
        </div>

        {#if filteredData}
          <!-- Controls Section -->
          <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="flex flex-col md:flex-row gap-6 items-start md:items-center">
              <!-- Filters -->
              <div class="flex flex-col sm:flex-row gap-3 flex-1">
                <div class="relative">
                  <select bind:value={major_option}
                          class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500
                                 transition-all cursor-pointer">
                    <option value="all">All Majors</option>
                    {#each majors as major}
                      <option value={major}>{major}</option>
                    {/each}
                  </select>
                </div>

                <div class="relative">
                  <select bind:value={year_option}
                          class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                 hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                 transition-all cursor-pointer">
                    <option value="all">All Years</option>
                    {#each years as year}
                      <option value={year}>{year}</option>
                    {/each}
                  </select>
                </div>

                {#if classes}
                  <div class="relative">
                    <select bind:value={class_option}
                            class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                   hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                   transition-all cursor-pointer">
                      <option value="all">All Classes</option>
                      {#each classes as inductionClass}
                        <option value={inductionClass.name}>{inductionClass.name}</option>
                      {/each}
                    </select>
                  </div>
                {/if}
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

          <!-- Data Section -->
          <div class="flex flex-col xl:flex-row gap-8">
            <!-- Main Table -->
            <div class="flex-1 overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
              <table class="w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    {#each headers as header}
                      <th on:click={() => sortBy(header)}
                          class="px-6 py-4 text-left text-sm font-semibold text-gray-700 cursor-pointer
                                 hover:bg-gray-100 transition-colors group">
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
                  {#each inducteeDataPerPage as inducteeData}
                    <tr class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        <a href="/profile/{inducteeData.user_id}" class="hover:underline">
                          {inducteeData.preferred_name}
                        </a>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{inducteeData.last_name}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{inducteeData.email}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{inducteeData.major}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700 font-mono">
                        {inducteeData.grad_year}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                        {inducteeData.induction_class}
                      </td>
                      {#each ['professional', 'social', 'technical', 'outreach', 'mentorship', 'general', 'total'] as category}
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700 font-medium font-mono">
                          {inducteeData[`${category}_points`]}
                        </td>
                      {/each}
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>

            <!-- Key Sidebar -->
             <!-- Legend Drawer -->
            <button
             on:click={() => showLegend = !showLegend}
             class="fixed right-0 top-1/2 z-40 bg-secondary p-2 rounded-l-lg shadow-md border border-gray-200 hover:bg-gray-50 transition-all"
           >
            <div
            class="fixed right-0 top-0 h-screen w-80 bg-white border-l border-gray-200 shadow-lg transform transition-transform duration-300 ease-in-out z-30"
            class:translate-x-full={!showLegend}
            >
            <div class="p-6">
            <h3 class="text-sm font-semibold text-gray-900 uppercase tracking-wide mb-4">Legend</h3>
            <div class="space-y-3">
                <div class="flex flex-col gap-3 justify-items-center p-2">
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-blue-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">Professional (P)</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-green-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">Social (S)</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-yellow-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">Technical (T)</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-red-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">Outreach (O)</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-purple-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">Mentorship (M)</span>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="w-2.5 h-2.5 bg-gray-600 rounded-full"></div>
                        <span class="text-sm text-gray-700">General (G)</span>
                    </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-100">
                    <p class="text-xs text-gray-500">
                        Points are calculated based on verified activities and events participation.
                    </p>
                    </div>
                </div>
            </div>
            </div>

          </div>

          <!-- Pagination -->
          <div class="mt-8">
            <Pagination rows={filteredData} perPage={15} bind:trimmedRows={inducteeDataPerPage} />
          </div>
        {:else}
          <div class="flex justify-center items-center h-96">
            <div class="animate-pulse flex items-center space-x-4">
              <div class="w-12 h-12 bg-blue-100 rounded-full"></div>
              <div class="space-y-2">
                <div class="h-4 bg-gray-100 rounded w-48"></div>
                <div class="h-4 bg-gray-100 rounded w-32"></div>
              </div>
            </div>
          </div>
        {/if}
      </div>

    {:else if $adminStatus == null}
      <div class="flex justify-center items-center h-screen bg-gray-50">
        <div class="flex flex-col items-center gap-4">
          <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-600">Verifying permissions...</p>
        </div>
      </div>

    {:else}
      <div class="flex justify-center items-center h-screen bg-gray-50">
        <div class="text-center space-y-4">
          <div class="inline-flex items-center gap-2 text-red-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h1 class="text-xl font-semibold">Unauthorized Access</h1>
          </div>
          <p class="text-gray-600 max-w-md px-4">
            You don't have permission to view this page. Please contact your system administrator if you believe this is an error.
          </p>
        </div>
      </div>
    {/if}
  </Layout>