<script>
    import Layout from "../Layout.svelte";
    import { onMount } from "svelte";

    let houses = [];
    let userHouse = null;
    let selectedHouse = null;
    let houseMembers = [];
    let pointsHistory = [];
    let isLoading = true;
    let activeTab = "leaderboard";
    let chartType = "line";

    // Variables for adding points
    let selectedMember = null;
    let pointsToAdd = 1;
    let pointsDescription = "";
    let isAddingPoints = false;
    let addPointsMessage = "";
    let addPointsError = "";

    // Fetch all houses for the leaderboard
    async function fetchHouses() {
        try {
            const response = await fetch("/api/house/leaderboard/");
            if (response.ok) {
                houses = await response.json();
                if (houses.length > 0 && !selectedHouse) {
                    selectedHouse = houses[0].name;
                    fetchHouseMembers(selectedHouse);
                    fetchPointsHistory(selectedHouse);
                }
            } else {
                console.error("Failed to fetch houses");
            }
        } catch (error) {
            console.error("Error fetching houses:", error);
        } finally {
            isLoading = false;
        }
    }

    // Fetch the current user's house
    async function fetchUserHouse() {
        try {
            const response = await fetch("/api/house/user/");
            if (response.ok) {
                userHouse = await response.json();
                if (userHouse && userHouse.is_leader) {
                    // If user is a house leader, fetch their house members
                    fetchHouseMembers(userHouse.house);
                }
            } else {
                console.log("User is not a member of any house");
            }
        } catch (error) {
            console.error("Error fetching user house:", error);
        }
    }

    // Fetch members of a specific house
    async function fetchHouseMembers(houseName) {
        try {
            const response = await fetch(`/api/house/members/${houseName}/`);
            if (response.ok) {
                houseMembers = await response.json();
            } else {
                console.error("Failed to fetch house members");
                houseMembers = [];
            }
        } catch (error) {
            console.error("Error fetching house members:", error);
            houseMembers = [];
        }
    }

    // Fetch points history for a specific house
    async function fetchPointsHistory(houseName) {
        try {
            const response = await fetch(`/api/house/history/${houseName}/`);
            if (response.ok) {
                pointsHistory = await response.json();
                drawChart();
            } else {
                console.error("Failed to fetch points history");
                pointsHistory = [];
            }
        } catch (error) {
            console.error("Error fetching points history:", error);
            pointsHistory = [];
        }
    }

    // Handle house selection change
    function handleHouseChange(houseName) {
        selectedHouse = houseName;
        fetchHouseMembers(houseName);
        fetchPointsHistory(houseName);
    }

    // Add points to a member
    async function addPointsToMember() {
        if (!selectedMember) {
            addPointsError = "Please select a member";
            return;
        }

        if (pointsToAdd <= 0) {
            addPointsError = "Points must be positive";
            return;
        }

        isAddingPoints = true;
        addPointsError = "";
        addPointsMessage = "";

        try {
            // Get CSRF token from cookies
            const csrftoken = getCookie('csrftoken');

            const response = await fetch(`/api/house/add-member-points/${selectedMember}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    points: pointsToAdd,
                    description: pointsDescription || "Points added by house leader"
                })
            });

            if (response.ok) {
                const data = await response.json();
                addPointsMessage = data.detail;

                // Reset form
                pointsToAdd = 1;
                pointsDescription = "";

                // Refresh data
                if (userHouse) {
                    fetchHouseMembers(userHouse.house);
                    fetchPointsHistory(userHouse.house);
                    fetchHouses(); // Refresh leaderboard
                }
            } else {
                const error = await response.json();
                addPointsError = error.detail || "Failed to add points";
            }
        } catch (error) {
            console.error("Error adding points:", error);
            addPointsError = "An error occurred while adding points";
        } finally {
            isAddingPoints = false;
        }
    }

    // Function to get cookie by name (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Draw chart using Google Charts
    function drawChart() {
        if (typeof google === 'undefined' || !google.visualization) {
            setTimeout(drawChart, 100);
            return;
        }

        if (pointsHistory.length === 0) return;

        const container = document.getElementById('chart_div');
        if (!container) return;

        if (chartType === "line") {
            drawLineChart();
        } else {
            drawBarChart();
        }
    }

    function drawLineChart() {
        const dataTable = new google.visualization.DataTable();
        dataTable.addColumn('date', 'Date');
        dataTable.addColumn('number', 'Points');
        dataTable.addColumn({type: 'string', role: 'tooltip'});

        // Add data rows
        pointsHistory.forEach(record => {
            const date = new Date(record.date);
            const formattedDate = date.toLocaleDateString();
            const tooltip = `${formattedDate}
${record.event}
${record.points} points earned by ${record.member?.name || 'House'}
Total: ${record.cumulative_points} points`;
            dataTable.addRow([date, record.cumulative_points, tooltip]);
        });

        const options = {
            title: `${selectedHouse} Points History`,
            titleTextStyle: {
                color: '#333',
                fontSize: 18,
                bold: true
            },
            curveType: 'function',
            legend: { position: 'none' },
            hAxis: {
                title: 'Date',
                format: 'MMM d, yyyy',
                gridlines: { color: '#f5f5f5' }
            },
            vAxis: {
                title: 'Points',
                minValue: 0,
                gridlines: { color: '#f5f5f5' }
            },
            colors: [getHouseColor(selectedHouse)],
            height: '100%',
            width: '100%',
            chartArea: { width: '85%', height: '75%' },
            backgroundColor: { fill: 'transparent' },
            animation: {
                startup: true,
                duration: 1000,
                easing: 'out'
            },
            pointSize: 5,
            lineWidth: 3,
            tooltip: { isHtml: true }
        };

        const chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(dataTable, options);
    }

    function drawBarChart() {
        // Get the house data for the bar chart
        const dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'House');
        dataTable.addColumn('number', 'Points');
        dataTable.addColumn({type: 'string', role: 'style'});
        dataTable.addColumn({type: 'string', role: 'tooltip'});

        houses.forEach(house => {
            const tooltip = `${house.name}\n${house.total_points} points\n${house.member_count} members`;
            dataTable.addRow([house.name, house.total_points, house.color, tooltip]);
        });

        const options = {
            title: 'House Points Leaderboard',
            titleTextStyle: {
                color: '#333',
                fontSize: 18,
                bold: true
            },
            legend: { position: 'none' },
            hAxis: {
                title: 'House',
                gridlines: { color: '#f5f5f5' }
            },
            vAxis: {
                title: 'Points',
                minValue: 0,
                gridlines: { color: '#f5f5f5' }
            },
            height: '100%',
            width: '100%',
            chartArea: { width: '85%', height: '75%' },
            backgroundColor: { fill: 'transparent' },
            animation: {
                startup: true,
                duration: 1000,
                easing: 'out'
            },
            bar: { groupWidth: '70%' },
            tooltip: { isHtml: true }
        };

        const chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(dataTable, options);
    }

    function getHouseColor(houseName) {
        const house = houses.find(h => h.name === houseName);
        return house ? house.color : 'Blue';
    }

    onMount(async () => {
        // Load Google Charts
        if (typeof google === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://www.gstatic.com/charts/loader.js';
            script.async = true;
            script.onload = () => {
                google.charts.load('current', {'packages':['corechart']});
                google.charts.setOnLoadCallback(() => {
                    fetchHouses();
                    fetchUserHouse();
                });
            };
            document.head.appendChild(script);
        } else {
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(() => {
                fetchHouses();
                fetchUserHouse();
            });
        }

        // Add resize listener
        window.addEventListener('resize', drawChart);
        return () => {
            window.removeEventListener('resize', drawChart);
        };
    });
</script>

<Layout>
    <div class="px-4 md:px-8 py-6 max-w-7xl mx-auto">
        <h1 class="text-4xl font-bold text-primary mb-6 animate-slide-up">House System</h1>

        {#if isLoading}
            <div class="flex justify-center items-center py-12">
                <div class="animate-pulse flex items-center space-x-4">
                    <div class="w-12 h-12 bg-blue-100 rounded-full"></div>
                    <div class="space-y-2">
                        <div class="h-4 bg-gray-100 rounded w-48"></div>
                        <div class="h-4 bg-gray-100 rounded w-32"></div>
                    </div>
                </div>
            </div>
        {:else}
            {#if userHouse}
                <div class="bg-gray-50 p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 mb-6 border border-gray-200">
                    <h2 class="text-2xl font-semibold">
                        Your House: <span style="color: {userHouse.color}">{userHouse.house}</span>
                    </h2>
                    <p class="mt-2 text-gray-700">Your Individual Points: <span class="font-semibold">{userHouse.individual_points}</span></p>
                    {#if userHouse.is_leader}
                        <span class="inline-block mt-2 bg-green-500 text-white text-sm px-3 py-1 rounded-full">
                            House Leader
                        </span>
                    {/if}
                </div>
            {/if}

            <div class="flex flex-wrap border-b border-gray-200 mb-6">
                <button
                    class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'leaderboard' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                    on:click={() => { activeTab = "leaderboard"; chartType = "bar"; drawChart(); }}>
                    House Leaderboard
                </button>
                <button
                    class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'history' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                    on:click={() => { activeTab = "history"; chartType = "line"; drawChart(); }}>
                    Points History
                </button>
                <button
                    class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'members' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                    on:click={() => { activeTab = "members"; }}>
                    House Members
                </button>
                {#if userHouse && userHouse.is_leader}
                    <button
                        class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'add-points' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                        on:click={() => { activeTab = "add-points"; }}>
                        Add Member Points
                    </button>
                {/if}
            </div>

            {#if activeTab === "leaderboard" || activeTab === "history"}
                <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
                    {#if activeTab === "history"}
                        <div class="flex flex-wrap items-center justify-between mb-6">
                            <div>
                                <h2 class="text-2xl font-semibold text-gray-800">Points History</h2>
                                <p class="text-gray-600 mt-1">Track the progress of {selectedHouse} over time</p>
                            </div>
                            <div class="flex items-center space-x-4">
                                <label for="house-select" class="font-medium text-gray-700">Select House:</label>
                                <select
                                    id="house-select"
                                    bind:value={selectedHouse}
                                    on:change={() => handleHouseChange(selectedHouse)}
                                    class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                           hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                           transition-all cursor-pointer">
                                    {#each houses as house}
                                        <option value={house.name}>{house.name}</option>
                                    {/each}
                                </select>
                            </div>
                        </div>

                        <!-- Recent Points Activity -->
                        {#if pointsHistory.length > 0}
                            <div class="mb-6">
                                <h3 class="text-lg font-medium text-gray-800 mb-3">Recent Activity</h3>
                                <div class="overflow-x-auto">
                                    <table class="min-w-full divide-y divide-gray-200">
                                        <thead class="bg-gray-50">
                                            <tr>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Member</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Added By</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {#each pointsHistory.slice(-5).reverse() as record}
                                                <tr class="hover:bg-gray-50">
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {new Date(record.date).toLocaleDateString()}
                                                    </td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.event}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{record.member?.name || 'House'}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">+{record.points}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{record.cumulative_points}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.added_by?.name || 'System'}</td>
                                                </tr>
                                            {/each}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        {/if}
                    {:else}
                        <div class="flex flex-wrap items-center justify-between mb-6">
                            <div>
                                <h2 class="text-2xl font-semibold text-gray-800">House Leaderboard</h2>
                                <p class="text-gray-600 mt-1">Current standings of all houses</p>
                            </div>
                        </div>

                        <!-- House Cards -->
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                            {#each houses.slice(0, 4) as house, i}
                                <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
                                    <div class="h-2" style="background-color: {house.color}"></div>
                                    <div class="p-4">
                                        <div class="flex items-center justify-between">
                                            <h3 class="text-lg font-semibold">{house.name}</h3>
                                            <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-100 text-gray-800 text-sm font-medium">
                                                {i + 1}
                                            </span>
                                        </div>
                                        <p class="text-2xl font-bold mt-2">{house.total_points} pts</p>
                                        <p class="text-gray-500 text-sm mt-1">{house.member_count} members</p>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}

                    <div class="h-[50vh]" id="chart_div"></div>
                </div>
            {:else if activeTab === "members" && selectedHouse}
                <div class="bg-white rounded-xl shadow-sm p-6">
                    <div class="mb-4">
                        <label for="house-select-members" class="font-medium text-gray-700 mr-2">Select House:</label>
                        <select
                            id="house-select-members"
                            bind:value={selectedHouse}
                            on:change={() => handleHouseChange(selectedHouse)}
                            class="pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                   hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                   transition-all cursor-pointer">
                            {#each houses as house}
                                <option value={house.name}>{house.name}</option>
                            {/each}
                        </select>
                    </div>

                    <h2 class="text-2xl font-semibold text-gray-800 mb-4">{selectedHouse} Members</h2>

                    {#if houseMembers.length === 0}
                        <p class="text-gray-600 py-4">No members found for this house.</p>
                    {:else}
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    {#each houseMembers as member, i}
                                        <tr class="hover:bg-gray-50">
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{i + 1}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{member.name}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{member.individual_points}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {#if member.is_leader}
                                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                        House Leader
                                                    </span>
                                                {:else}
                                                    Member
                                                {/if}
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    {/if}
                </div>
            {:else if activeTab === "add-points" && userHouse && userHouse.is_leader}
                <div class="bg-white rounded-xl shadow-sm p-6">
                    <h2 class="text-2xl font-semibold text-gray-800 mb-4">Add Points to House Members</h2>

                    {#if addPointsMessage}
                        <div class="mb-4 p-3 bg-green-100 text-green-800 rounded-lg">
                            {addPointsMessage}
                        </div>
                    {/if}

                    {#if addPointsError}
                        <div class="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                            {addPointsError}
                        </div>
                    {/if}

                    <form on:submit|preventDefault={addPointsToMember} class="space-y-4">
                        <div>
                            <label for="member-select" class="block text-sm font-medium text-gray-700 mb-1">Select Member</label>
                            <select
                                id="member-select"
                                bind:value={selectedMember}
                                class="w-full pl-4 pr-8 py-2 rounded-lg border border-gray-200 text-gray-700
                                       hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                       transition-all cursor-pointer overflow-hidden">
                                <option value={null}>Select a member</option>
                                {#each houseMembers as member}
                                    <option value={member.user_id}>{member.name}</option>
                                {/each}
                            </select>
                        </div>

                        <div>
                            <label for="points-input" class="block text-sm font-medium text-gray-700 mb-1">Points to Add</label>
                            <input
                                id="points-input"
                                type="number"
                                min="0.5"
                                step="0.5"
                                bind:value={pointsToAdd}
                                class="w-full pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                       hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                       transition-all"
                            />
                        </div>

                        <div>
                            <label for="description-input" class="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                            <textarea
                                id="description-input"
                                bind:value={pointsDescription}
                                placeholder="Reason for adding points"
                                class="w-full pl-4 pr-4 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                       hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                       transition-all"
                                rows="3"
                            ></textarea>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={isAddingPoints}
                                class="px-4 py-2 bg-primary hover:bg-secondary text-white font-medium rounded-lg
                                       transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary
                                       disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isAddingPoints ? 'Adding Points...' : 'Add Points'}
                            </button>
                        </div>
                    </form>

                    <div class="mt-8">
                        <h3 class="text-lg font-medium text-gray-800 mb-2">House Members</h3>
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Points</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    {#each houseMembers.filter(m => !m.is_leader) as member}
                                        <tr class="hover:bg-gray-50 cursor-pointer" on:click={() => selectedMember = member.user_id}>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{member.name}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{member.individual_points}</td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</Layout>