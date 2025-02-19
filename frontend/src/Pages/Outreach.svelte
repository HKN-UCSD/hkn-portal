<script>
    import Layout from "../Layout.svelte";
    import { onMount } from 'svelte';
    import {adminStatus} from '../stores.js';
    import Pagination from "../Components/Pagination.svelte";
    import SearchBar from "../Components/SearchBar.svelte";

    let outreachData;
    let filteredData;
    let searchText = "";

    async function getOutreach() {
        let response = await fetch(`/api/outreach/`);
        if (response.status === 200) {
            let users = await response.json();
            users = users.sort((first, second) => {
                if (first['last_name'] < second['last_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
            return users;
        } else {
            throw new Error(response.statusText);
        }
    }

    async function getAdminStatus() {
        let response = await fetch(`/api/permissions/`);
        if (response.status === 200) {
            let output = await response.json();
            return output.is_admin;
        } else {
            throw new Error(response.statusText);
        }
    }

    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'hours', "title": "Hours"},
        {"value": 'car', "title": 'Car'},
        {"value": 'outreach_course', "title": "Class"},
        {"value": 'quarter', "title": "Quarter"}
    ]



    let classes = [
        'CSE',
        'ECE',
        'MAE'
    ]

    let cars = [
        'Yes',
        'No'
    ]
    let quarters = []


    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;
        } else {
            ascending = true;
        }
        sorting_col = header["value"];

        if (ascending) {
            outreachData = outreachData.sort((first, second) => {
                if (first[sorting_col] < second[sorting_col]) {
                    return -1;
                } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                    return -1;
                } else {
                    return 0;
                }
            })
        } else {
            outreachData = outreachData.sort((first, second) => {
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

    let class_option;
    let car_option;
    let quarter_option;

    let csv_data;
    let outreachDataPerPage = [];

    function tableToCSV() {

        // Variable to store the final csv data
        csv_data = [];

        // Get each row data
        var rows = document.getElementsByTagName('tr');
        for (var i = 0; i < rows.length; i++) {

            // Get each column data
            var cols = rows[i].querySelectorAll('td,th');

            // Stores each csv row data
            var csvrow = [];
            for (var j = 0; j < cols.length; j++) {

                // Get the text data of each cell
                // of a row and push it to csvrow
                if (j == 0 && i != 0) {
                    var element = cols[j].querySelector('a');
                    csvrow.push(element.innerHTML);
                } else {
                    csvrow.push(cols[j].innerHTML);
                }
            }

            // Combine each column value with comma
            csv_data.push(csvrow.join(","));
        }

        // Combine each row data with new line character
        csv_data = csv_data.join('\n');

    }


    function download_table() {
        tableToCSV();
        var textToSave = csv_data;
        var hiddenElement = document.createElement('a');

        hiddenElement.href = 'data:attachment/text,' + encodeURI(textToSave);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'outreach_students.csv';
        hiddenElement.click();
    }
    function filter() {
        filteredData = outreachData.filter((outreachStudent) => {
            return (class_option == "all" || outreachStudent.outreach_course == class_option)
                && (car_option == "all" || outreachStudent.car == car_option)
                && (quarter_option == "all" || outreachStudent.quarter == quarter_option)
                && ((outreachStudent.preferred_name.toLowerCase() + " " + outreachStudent.last_name.toLowerCase()).includes(searchText.toLowerCase())
                    || outreachStudent.email.toLowerCase().includes(searchText.toLowerCase()));
        })

    }
    onMount(async () => {
        outreachData = await getOutreach();

        quarters = outreachData.map((outreachStudent) => {
            return outreachStudent.quarter;
        })
        quarters = [...new Set(quarters)];


    })
    $: {
        car_option, class_option, searchText, quarter_option;
        if (outreachData) filter();
        }
</script>
<svelte:head>
    <title> HKN Portal | Outreach Students </title>
</svelte:head>
<Layout>
    {#if $adminStatus === true}
      <div class="px-8 py-8 max-w-screen-2xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Outreach Students</h1>
          <p class="mt-2 text-gray-600">Manage and view outreach student records</p>
        </div>

        {#if filteredData}
          <!-- Controls Section -->
          <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="flex flex-col md:flex-row gap-6 items-start md:items-center">
              <!-- Filters -->
              <div class="flex flex-col sm:flex-row gap-3 flex-1">
                <div class="relative">
                  <select bind:value={class_option}
                          class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500
                                 transition-all cursor-pointer">
                    <option value="all">Filter by Class</option>
                    {#each classes as curr_class}
                      <option value={curr_class}>{curr_class}</option>
                    {/each}
                  </select>
                </div>

                <div class="relative">
                  <select bind:value={car_option}
                          class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500
                                 transition-all cursor-pointer">
                    <option value="all">Filter by Car</option>
                    {#each cars as car}
                      <option value={car}>{car}</option>
                    {/each}
                  </select>
                </div>

                <div class="relative">
                  <select bind:value={quarter_option}
                          class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                 hover:border-gray-300 focus:ring-2 focus:ring-blue-200 focus:border-blue-500
                                 transition-all cursor-pointer">
                    <option value="all">Filter by Quarter</option>
                    {#each quarters as quarter}
                      <option value={quarter}>{quarter}</option>
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

          <!-- Data Table -->
          <div class="overflow-x-auto rounded-xl border border-gray-100 bg-white shadow-sm">
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
                {#each outreachDataPerPage as outreachStudent}
                  <tr class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      {#if adminStatus}
                        <a href="/profile/{outreachStudent.user_id}" class="hover:underline">
                          {outreachStudent.preferred_name}
                        </a>
                      {:else}
                        {outreachStudent.preferred_name}
                      {/if}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{outreachStudent.last_name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{outreachStudent.email}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700 font-mono">
                      {outreachStudent.hours}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                      {outreachStudent.car}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                      {outreachStudent.outreach_course}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                      {outreachStudent.quarter}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div class="mt-8">
            <Pagination rows={filteredData} perPage={15} bind:trimmedRows={outreachDataPerPage} />
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

