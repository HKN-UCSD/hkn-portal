<script>
    import Layout from "../Layout.svelte";
    import Pagination from "../Components/Pagination.svelte";
    import { onDestroy, onMount } from "svelte";
    import { memberStatus, adminStatus } from '../stores.js';
    import SearchBar from "../Components/SearchBar.svelte";
    import { slide } from "svelte/transition";

    async function getMajors() {
        return await (await(fetch(`api/majors/`))).json()
    }

    let majors = [];
    let years = [];

    async function getMembers() {
        let timestamp = new Date().getTime();
        let response = await fetch(`/api/members/?t=${timestamp}`);
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
            output.sort((a, b) => new Date(b.start_date) - new Date(a.start_date));
            return output;
        } else {
            throw new Error(response.statusText);
        }
    }

    let canFilter = false;
    let current_courses = [];

    async function fetchCurrentCourses() {
        try{
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
                    const user = await response.json();
                    current_courses = user.current_courses || [];
                    canFilter = current_courses.length > 0; 
                } else {
                    console.error("Failed to fetch user data");
                }
            } catch (error) {
                console.error("Error fetching user data:", error);
        }
    }



    let headers = [
        {"value": 'preferred_name', "title": 'First Name'},
        {"value": 'last_name', "title": 'Last Name'},
        {"value": 'email', "title": "Email"},
        {"value": 'major', "title": 'Major'},
        {"value": 'grad_year', "title": 'Year'},
        {"value": 'induction_class', "title": 'Class'},
        {"value": 'social_links', "title": 'Social Links'},
        {"value": 'current_courses', "title": 'Courses'},
    ]

    const sortBy = (header) => {
        if (sorting_col == header["value"]) {
            ascending = !ascending;

        } else {
            ascending = true;
        }
        sorting_col = header["value"];
        if (sorting_col === "social_links") {
            // Special handling for social links sorting
            filteredData = filteredData.sort((first, second) => {
                // Count how many social links each member has
                const firstLinkCount = first.social_links ? 
                    Object.values(first.social_links).filter(link => link && link.username).length : 0;
                const secondLinkCount = second.social_links ? 
                    Object.values(second.social_links).filter(link => link && link.username).length : 0;
                
                if (ascending) {
                    // Sort by number of links (ascending)
                    return firstLinkCount - secondLinkCount;
                } else {
                    // Sort by number of links (descending)
                    return secondLinkCount - firstLinkCount;
                }
            });
        } else {
            if (ascending) {
                membersData = membersData.sort((first, second) => {
                    if (first[sorting_col] < second[sorting_col]) {
                        return -1;
                    } else if (first[sorting_col] == second[sorting_col] && first['preferred_name'] < second['preferred_name']) {
                        return -1;
                    } else {
                        return 0;
                    }
                })
            } else {
                membersData = membersData.sort((first, second) => {
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
    }

    let sorting_col = "N/A";
    let ascending = true;

    let major_option;
    let year_option;
    let class_option
    let searchText = "";
    let filteredData;

    let showFilterWarning = false;

    // Function for filtering and searching
    function filter() {
        let preFiltered = membersData;

        let searchTextFilter = searchText.toLowerCase().trim();

        // Apply all filters
        filteredData = preFiltered.filter(memberData => {
            if (canFilter) {
                return (major_option == "all" || memberData.major == major_option || major_option == "Other" && !majors.includes(memberData.major))
                    && (year_option == "all" || memberData.grad_year == parseInt(year_option))
                    && (class_option == "all" || memberData.induction_class == class_option)
                    && (searchText == "" || (
                        (memberData.preferred_name.toLowerCase() + " " + memberData.last_name.toLowerCase()).includes(searchTextFilter) ||
                        memberData.email.toLowerCase().includes(searchText.toLowerCase()) ||
                        (memberData.current_courses && memberData.current_courses.some(course =>
                            course.replace(/\s/g, '').toLowerCase().includes(searchTextFilter.replace(/\s/g, ''))
                        ))
                    ));
            } else {
                return (major_option == "all" || memberData.major == major_option || major_option == "Other" && !majors.includes(memberData.major))
                    && (year_option == "all" || memberData.grad_year == parseInt(year_option))
                    && (class_option == "all" || memberData.induction_class == class_option)
                    && (searchText == "" || (
                        (memberData.preferred_name.toLowerCase() + " " + memberData.last_name.toLowerCase()).includes(searchTextFilter) ||
                        memberData.email.toLowerCase().includes(searchText.toLowerCase())
                    ));
            }
        });
    }

    let membersData, classes;
    let memberDataPerPage = [];
    let userIsMember = false;
    const unsubscribe = memberStatus.subscribe(value => {
        userIsMember = value;
    });
    
    onDestroy(() => {
        if(unsubscribe) {
            unsubscribe();
        }
    });

    onMount(async () => {
        if (memberStatus || adminStatus) {
            await fetchCurrentCourses();
            membersData = await getMembers();
            classes = await getInductionClasses();

            // URL query from profile page
            const urlParams = new URLSearchParams(window.location.search);
            const searchQuery = urlParams.get('search');
            if (searchQuery) {
                searchText = searchQuery;
            }
        }
    });
    
    // filter the data when the membersData and classes are loaded if any of the options changes
    $: {
        major_option, year_option, class_option, searchText;
        if (membersData && classes) filter();
    }
</script>

<svelte:head>
    <title>HKN Portal | Members</title>
</svelte:head>

<Layout>
    {#if memberStatus || adminStatus}
        <div class="px-8 py-8 max-w-screen-2xl mx-auto">
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">Members</h1>
                <p class="mt-2 text-gray-600">Connect with other HKN members</p>
            </div>

            {#if filteredData}
                <!-- Controls Section -->
                <section class="mb-8 p-6 bg-white rounded-xl shadow-sm border border-gray-100">
                    <div class="flex flex-col md:flex-row items-start md:items-center gap-6 flex-wrap justify-between">
                        <!-- Filters -->
                        <div class="flex flex-wrap gap-x-3 gap-y-4 items-start md:items-center">
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
                        <!-- Search-->
                        <div class="w-full md:w-80">
                            <SearchBar bind:searchText
                                placeholder="Search courses, names, or emails..."
                                className="md:w-80 max-w-md rounded-lg" />
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
                        {#each memberDataPerPage as memberData}
                            <tr class="hover:bg-gray-50 transition-colors">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                                <a href="/profile/{memberData.user_id}" class="hover:underline">
                                {memberData.preferred_name}
                                </a>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{memberData.last_name}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{memberData.email}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{memberData.major}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700 font-mono">
                                {memberData.grad_year}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                                {memberData.induction_class}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-700">
                                <div class="flex justify-center gap-2">
                                    {#each Object.entries(memberData.social_links) as [platform, data]}
                                        {#if data.username}
                                        <a href={data.link + data.username} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            class="hover:opacity-80 transition-opacity">
                                            <img src={`/static/${platform.toLowerCase()}.png`}
                                                class="h-5 w-5"
                                                alt="{platform} Logo">
                                        </a>
                                        {/if}
                                    {/each}
                                </div>
                            </td>
                            <td class="content-center">
                                {#if canFilter}
                                    {#each memberData.current_courses.slice(0, 4) as course}
                                        <div class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs w-[8em] text-center my-1">
                                            {course}
                                        </div>
                                    {/each}
                                {/if}
                                {#if memberData.current_courses.length > 4}
                                    <a href="/profile/{memberData.user_id}" class="text-xs text-blue-500 italic mt-1 hover:underline block">
                                        +{memberData.current_courses.length - 4} more
                                    </a>
                                {/if}
                            </td>
                            </tr>
                        {/each}
                        </tbody>
                    </table>
                    </div>
                </div>

                <!-- Pagination -->
                <div class="mt-8">
                    <Pagination rows={filteredData} perPage={15} bind:trimmedRows={memberDataPerPage} />
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

        {#if !canFilter}
            <div class="fixed bottom-4 right-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded shadow-md">
                <div class="flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M12 18h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
                    </svg>
                    <span>Please input your courses in profile to use the course search function</span>
                </div>
            </div>
        {/if}
    {:else}
        <div class="flex justify-center items-center h-screen bg-gray-50">
            <div class="text-center space-y-4 max-w-md px-6">
                <div class="inline-flex items-center gap-2 text-red-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h1 class="text-xl font-semibold">You do not have permission</h1>
                </div>
                <p class="text-gray-600">
                    This page is only available to HKN members. Interested in joining?
                </p>
                <a href="https://hkn.ucsd.edu/hkn-membership/" class="inline-block mt-4 px-6 py-2 bg-secondary hover:bg-primary text-white rounded-lg transition-all hover:translate-y-[-1px]">
                    Learn about induction
                </a>
            </div>
        </div>
    {/if}
</Layout>
