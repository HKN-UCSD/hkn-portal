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
    let chartType = "bar";

    // Variables for adding points
    let selectedMember = null;
    let pointsToAdd = 1;
    let pointsDescription = "";
    let isAddingPoints = false;
    let addPointsMessage = "";
    let addPointsError = "";

    // Variables for adding house members
    let availableUsers = [];
    let newMemberUserId = null;
    let isAddingMember = false;
    let addMemberMessage = "";
    let addMemberError = "";
    let userSearchQuery = "";
    let filteredAvailableUsers = [];
    let showUserDropdown = false;
    let selectedUser = null;

    // Variables for deleting house members
    let memberToDelete = null;
    let showDeleteMemberModal = false;
    let isDeletingMember = false;
    let deleteMemberMessage = "";
    let deleteMemberError = "";

    // Variables for editing point records
    let editingRecord = null;
    let editPoints = 0;
    let editDescription = "";
    let isEditingPoints = false;
    let editPointsMessage = "";
    let editPointsError = "";
    let showEditModal = false;
    let showDeleteConfirmModal = false;
    let deletingRecord = null;
    let isDeletingPoints = false;

    // Variables for checking User points
    let userPointHistory = [];
    let showUserHistoryModal = false;
    let selectedUserName = "";
    let isFetchingUserHistory = false;
    let userHistoryError = "";

    // Variables for sync
    let showSyncPopup = false;
    let syncMessage = "";

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
                // Add a small delay to ensure the DOM is ready before drawing the chart
                setTimeout(() => {
                    drawChart();
                }, 100);
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
                    // Also fetch available users to add to the house
                    fetchAvailableUsers();
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
                // Note: individual_points are now calculated dynamically from point records
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
                // Add a small delay to ensure the DOM is ready before drawing the chart
                setTimeout(() => {
                    drawChart();
                }, 100);
            } else {
                console.error("Failed to fetch points history");
                pointsHistory = [];
            }
        } catch (error) {
            console.error("Error fetching points history:", error);
            pointsHistory = [];
        }
    }

    // Fetch available users to add to the house
    async function fetchAvailableUsers() {
        try {
            const response = await fetch("/api/users/");
            if (response.ok) {
                const allUsers = await response.json();
                // Filter out users who are already in a house
                const houseMemberIds = houseMembers.map(member => member.user_id);
                availableUsers = allUsers.filter(user => !houseMemberIds.includes(user.user_id));
                filterUsers(); // Initialize filtered users
            } else {
                console.error("Failed to fetch available users");
                availableUsers = [];
                filteredAvailableUsers = [];
            }
        } catch (error) {
            console.error("Error fetching available users:", error);
            availableUsers = [];
            filteredAvailableUsers = [];
        }
    }

    async function fetchUserPointHistory(userId, userName) {
        isFetchingUserHistory = true;
        userHistoryError = "";
        userPointHistory = [];
        selectedUserName = userName;
        showUserHistoryModal = true;

        try {
            const response = await fetch(`/api/users/${userId}/point-history/`);
            if (response.ok) {
                userPointHistory = await response.json();
            } else {
                const error = await response.json();
                userHistoryError = error.detail || "Failed to fetch history";
            }
        } catch (error) {
            console.error("Error fetching user point history:", error);
            userHistoryError = "An unexpected error occurred.";
        } finally {
            isFetchingUserHistory = false;
        }
    }

    // Filter users based on search query
    function filterUsers() {
        if (!userSearchQuery) {
            filteredAvailableUsers = availableUsers;
            return;
        }

        const query = userSearchQuery.toLowerCase();
        filteredAvailableUsers = availableUsers.filter(user =>
            user.preferred_name.toLowerCase().includes(query) ||
            user.last_name.toLowerCase().includes(query) ||
            `${user.preferred_name} ${user.last_name}`.toLowerCase().includes(query)
        );
    }

    // Handle user selection
    function handleUserSelection(user) {
        selectedUser = user;
        newMemberUserId = user.user_id;
        userSearchQuery = "";
        showUserDropdown = false;
    }

    // Clear selected user
    function clearSelectedUser() {
        selectedUser = null;
        newMemberUserId = null;
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

    // Add a new member to the house
    async function addHouseMember() {
        if (!newMemberUserId) {
            addMemberError = "Please select a user";
            return;
        }

        isAddingMember = true;
        addMemberError = "";
        addMemberMessage = "";

        try {
            // Get CSRF token from cookies
            const csrftoken = getCookie('csrftoken');

            const response = await fetch("/api/house-memberships/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    user: newMemberUserId,
                    house: userHouse.house,
                    is_house_leader: false
                })
            });

            if (response.ok) {
                const data = await response.json();
                addMemberMessage = `Added user to ${userHouse.house} house`;

                // Reset form
                clearSelectedUser();
                userSearchQuery = "";

                // Refresh data
                fetchHouseMembers(userHouse.house);
                fetchAvailableUsers();
            } else {
                const error = await response.json();
                addMemberError = error.detail || "Failed to add member";
            }
        } catch (error) {
            console.error("Error adding member:", error);
            addMemberError = "An error occurred while adding member";
        } finally {
            isAddingMember = false;
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

        // Ensure we have data to display
        if ((chartType === "line" && pointsHistory.length === 0) ||
            (chartType === "bar" && houses.length === 0)) {
            return;
        }

        const container = document.getElementById('chart_div');
        if (!container) {
            // If container is not ready, try again after a short delay
            setTimeout(drawChart, 100);
            return;
        }

        // Ensure chart type matches active tab
        if (activeTab === "leaderboard" && chartType !== "bar") {
            chartType = "bar";
        } else if (activeTab === "history" && chartType !== "line") {
            chartType = "line";
        }

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
            curveType: 'none',
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

    // Open edit modal for a record
    function openEditModal(record) {
        editingRecord = record;
        editPoints = record.points;
        editDescription = record.description || "";
        showEditModal = true;
    }

    // Open delete confirmation modal
    function openDeleteModal(record) {
        deletingRecord = record;
        showDeleteConfirmModal = true;
    }

    // Edit a point record
    async function editPointRecord() {
        if (!editingRecord) return;

        if (editPoints <= 0) {
            editPointsError = "Points must be positive";
            return;
        }

        isEditingPoints = true;
        editPointsError = "";
        editPointsMessage = "";

        try {
            // Get CSRF token from cookies
            const csrftoken = getCookie('csrftoken');

            // Check if the record has an id property
            if (!editingRecord.id) {
                console.error("Record ID is missing:", editingRecord);
                editPointsError = "Record ID is missing. Cannot update record.";
                isEditingPoints = false;
                return;
            }

            const response = await fetch(`/api/house/edit-point-record/${editingRecord.id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify({
                    points: editPoints,
                    description: editDescription
                })
            });

            if (response.ok) {
                const data = await response.json();
                editPointsMessage = data.detail;
                showEditModal = false;

                // Refresh data
                fetchPointsHistory(selectedHouse);
                fetchHouses(); // Refresh leaderboard
                if (userHouse) {
                    fetchHouseMembers(userHouse.house);
                }
            } else {
                const error = await response.json();
                editPointsError = error.detail || "Failed to update points";
            }
        } catch (error) {
            console.error("Error updating points:", error);
            editPointsError = "An error occurred while updating points";
        } finally {
            isEditingPoints = false;
        }
    }

    // Delete a point record
    async function deletePointRecord() {
        if (!deletingRecord) return;

        // Check if the record has an id property
        if (!deletingRecord.id) {
            console.error("Record ID is missing:", deletingRecord);
            addPointsError = "Record ID is missing. Cannot delete record.";
            showDeleteConfirmModal = false;
            return;
        }

        isDeletingPoints = true;

        try {
            // Get CSRF token from cookies
            const csrftoken = getCookie('csrftoken');

            const response = await fetch(`/api/house/delete-point-record/${deletingRecord.id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            });

            if (response.ok) {
                const data = await response.json();
                addPointsMessage = data.detail;
                showDeleteConfirmModal = false;

                // Refresh data
                fetchPointsHistory(selectedHouse);
                fetchHouses(); // Refresh leaderboard
                if (userHouse) {
                    fetchHouseMembers(userHouse.house);
                }
            } else {
                const error = await response.json();
                addPointsError = error.detail || "Failed to delete points";
            }
        } catch (error) {
            console.error("Error deleting points:", error);
            addPointsError = "An error occurred while deleting points";
        } finally {
            isDeletingPoints = false;
            deletingRecord = null;
        }
    }

    // Delete a house member
    async function deleteMember() {
        if (!memberToDelete) return;

        isDeletingMember = true;
        deleteMemberError = "";
        deleteMemberMessage = "";

        try {
            // Get CSRF token from cookies
            const csrftoken = getCookie('csrftoken');

            const response = await fetch(`/api/house-memberships/${memberToDelete.user_id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            });

            if (response.ok) {
                deleteMemberMessage = `Removed ${memberToDelete.name} from ${userHouse.house} house. Their ${memberToDelete.individual_points} points have been removed from the house total.`;
                showDeleteMemberModal = false;

                // Refresh data
                fetchHouseMembers(userHouse.house);
                fetchAvailableUsers();
                fetchHouses(); // Refresh leaderboard
            } else {
                const error = await response.json();
                deleteMemberError = error.detail || "Failed to remove member";
            }
        } catch (error) {
            console.error("Error removing member:", error);
            deleteMemberError = "An error occurred while removing member";
        } finally {
            isDeletingMember = false;
            memberToDelete = null;
        }
    }

    // Open delete member confirmation modal
    function openDeleteMemberModal(member) {
        memberToDelete = member;
        showDeleteMemberModal = true;
    }

    // Sync house points
    async function syncHousePoints() {
        syncMessage = "Syncing...";
        showSyncPopup = true;

        try {
            const csrftoken = getCookie('csrftoken');
            const response = await fetch("/api/house/sync/", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                }
            });

            if (response.ok) {
                const data = await response.json();
                syncMessage = data.detail || "Sync successful!";
                // Keep popup open longer for successful sync
                setTimeout(() => {
                    showSyncPopup = false;
                }, 3000);
            } else {
                const error = await response.json();
                syncMessage = error.detail || "Sync failed";
                // Keep popup open longer for errors
                setTimeout(() => {
                    showSyncPopup = false;
                }, 5000);
            }
        } catch (error) {
            console.error("Error syncing points:", error);
            syncMessage = "An error occurred during sync";
            setTimeout(() => {
                showSyncPopup = false;
            }, 5000);
        }
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
                    // Ensure chartType matches activeTab on initial load
                    chartType = activeTab === "leaderboard" ? "bar" : "line";
                    fetchHouses();
                    fetchUserHouse();
                    // Add a delay to ensure everything is loaded before drawing the chart
                    setTimeout(() => {
                        drawChart();
                    }, 300);
                });
            };
            document.head.appendChild(script);
        } else {
            google.charts.load('current', {'packages':['corechart']});
            google.charts.setOnLoadCallback(() => {
                // Ensure chartType matches activeTab on initial load
                chartType = activeTab === "leaderboard" ? "bar" : "line";
                fetchHouses();
                fetchUserHouse();
                // Add a delay to ensure everything is loaded before drawing the chart
                setTimeout(() => {
                    drawChart();
                }, 300);
            });
        }

        // Add resize listener
        window.addEventListener('resize', () => {
            // Add a small delay before redrawing on resize
            setTimeout(() => {
                drawChart();
            }, 100);
        });

        // Close dropdown when clicking outside
        const handleClickOutside = (event) => {
            if (showUserDropdown && !event.target.closest('.user-search-container')) {
                showUserDropdown = false;
            }
        };

        document.addEventListener('click', handleClickOutside);

        return () => {
            window.removeEventListener('resize', drawChart);
            document.removeEventListener('click', handleClickOutside);
        };
    });
    </script>

<Layout>
    <div class="px-4 md:px-8 py-6 max-w-7xl mx-auto">
<!--         <h1 class="text-4xl font-bold text-primary mb-6 animate-slide-up">House System</h1>
 -->
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
            <div class="bg-gray-50 p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 mb-6 border border-gray-200">
                <div class="flex items-center justify-between mb-2">
                    <h2 class="text-2xl font-semibold">
                        Your House: <span class="text-gray-500">{userHouse ? userHouse.house : 'No House'}</span>
                    </h2>
                    <button
                        on:click={syncHousePoints}
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600">
                        Sync
                    </button>
                </div>
                <p class="mt-2 text-gray-700">Your Individual Points: <span class="font-semibold">{userHouse ? userHouse.individual_points : 0}</span></p>
                {#if userHouse && userHouse.is_leader}
                    <span class="inline-block mt-2 bg-green-500 text-white text-sm px-3 py-1 rounded-full">
                        House Leader
                    </span>
                {/if}
            </div>

            <div class="flex flex-wrap border-b border-gray-200 mb-6">
                <button
                    class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'leaderboard' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                    on:click={() => {
                        activeTab = "leaderboard";
                        chartType = "bar";
                        // Add a small delay to ensure the DOM is ready before drawing the chart
                        setTimeout(() => {
                            drawChart();
                        }, 100);
                    }}>
                    House Leaderboard
                </button>
                <button
                    class="px-6 py-3 font-medium text-gray-700 hover:text-primary focus:outline-none {activeTab === 'history' ? 'border-b-2 border-primary text-primary font-semibold' : ''}"
                    on:click={() => {
                        activeTab = "history";
                        chartType = "line";
                        // Add a small delay to ensure the DOM is ready before drawing the chart
                        setTimeout(() => {
                            drawChart();
                        }, 100);
                    }}>
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
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Points</th>
                                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                                            </tr>
                                        </thead>
                                        <tbody class="bg-white divide-y divide-gray-200">
                                            {#each pointsHistory.slice(-10).reverse() as record, i}
                                                <tr class="hover:bg-gray-50">
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {new Date(record.date).toLocaleDateString()}
                                                    </td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{record.event}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">+{record.points}</td>
                                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{record.cumulative_points}</td>
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

                    {#if userHouse && userHouse.is_leader && userHouse.house === selectedHouse}
                        <div class="mb-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
                            <h3 class="text-lg font-medium text-gray-800 mb-4">Add New House Member</h3>

                            {#if addMemberMessage}
                                <div class="mb-4 p-3 bg-green-100 text-green-800 rounded-lg">
                                    {addMemberMessage}
                                </div>
                            {/if}

                            {#if addMemberError}
                                <div class="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                                    {addMemberError}
                                </div>
                            {/if}

                            <form on:submit|preventDefault={addHouseMember} class="space-y-4">
                                <div>
                                    <label for="user-search-select" class="block text-sm font-medium text-gray-700 mb-1">Search and Select User</label>
                                    <div class="relative w-full user-search-container">
                                        <div class="flex flex-wrap items-center w-full p-2 border border-gray-200 rounded-lg bg-white">
                                            {#if selectedUser}
                                                <div class="flex items-center bg-gray-100 text-gray-800 text-sm px-3 py-1 rounded-lg mr-2">
                                                    <span>{selectedUser.preferred_name} {selectedUser.last_name}</span>
                                                    <button
                                                        type="button"
                                                        class="ml-2 text-gray-500 hover:text-red-500"
                                                        on:click={clearSelectedUser}
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                            {/if}
                                            <input
                                                id="user-search-select"
                                                type="text"
                                                bind:value={userSearchQuery}
                                                on:input={filterUsers}
                                                on:focus={() => showUserDropdown = true}
                                                placeholder={selectedUser ? "" : "Search for a user..."}
                                                class="flex-grow py-1 px-2 bg-transparent border-none outline-none focus:ring-0"
                                            />
                                            <div class="flex items-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                                </svg>
                                            </div>
                                        </div>

                                        {#if showUserDropdown && filteredAvailableUsers.length > 0}
                                            <div class="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                                                {#each filteredAvailableUsers as user}
                                                <!-- svelte-ignore a11y-click-events-have-key-events -->
                                                    <div
                                                        class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                                                        on:click={() => handleUserSelection(user)}
                                                    >
                                                        {user.preferred_name} {user.last_name}
                                                    </div>
                                                {/each}
                                            </div>
                                        {:else if showUserDropdown && userSearchQuery && filteredAvailableUsers.length === 0}
                                            <div class="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg">
                                                <div class="px-4 py-2 text-sm text-red-600">
                                                    No users found matching "{userSearchQuery}"
                                                </div>
                                            </div>
                                        {:else if showUserDropdown && filteredAvailableUsers.length === 0}
                                            <div class="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg">
                                                <div class="px-4 py-2 text-sm text-gray-500">
                                                    No available users to add
                                                </div>
                                            </div>
                                        {/if}
                                    </div>
                                </div>

                                <div>
                                    <button
                                        type="submit"
                                        disabled={isAddingMember || !newMemberUserId}
                                        class="px-4 py-2 bg-primary hover:bg-secondary text-white font-medium rounded-lg
                                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary
                                               disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isAddingMember ? 'Adding Member...' : 'Add to House'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    {/if}

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
                                        {#if userHouse && userHouse.is_leader && userHouse.house === selectedHouse}
                                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                        {/if}
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    {#each houseMembers as member, i}
                                        <tr class="hover:bg-gray-50">
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{i + 1}</td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            <span
                                                role="button"
                                                tabindex="0"
                                                on:click={() => fetchUserPointHistory(member.user_id, member.name)}
                                                on:keydown={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') {
                                                    e.preventDefault();
                                                    fetchUserPointHistory(member.user_id, member.name);
                                                }
                                                }}
                                                class="text-black-600 hover:underline cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                                            >
                                                {member.name}
                                            </span>
                                            </td>
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
                                            {#if userHouse && userHouse.is_leader && userHouse.house === selectedHouse && !member.is_leader}
                                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    <button
                                                        on:click={() => openDeleteMemberModal(member)}
                                                        class="text-red-600 hover:text-red-800"
                                                        title="Remove member">
                                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                        </svg>
                                                    </button>
                                                </td>
                                            {:else if userHouse && userHouse.is_leader && userHouse.house === selectedHouse}
                                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    <!-- Empty cell for house leaders -->
                                                </td>
                                            {/if}
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>

                        {#if deleteMemberMessage}
                            <div class="mt-4 p-3 bg-green-100 text-green-800 rounded-lg">
                                {deleteMemberMessage}
                            </div>
                        {/if}

                        {#if deleteMemberError}
                            <div class="mt-4 p-3 bg-red-100 text-red-800 rounded-lg">
                                {deleteMemberError}
                            </div>
                        {/if}
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
                                       transition-all cursor-pointer"
                            >
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

    <!-- Edit Point Record Modal -->
    {#if showEditModal}
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Edit Point Record</h3>

                {#if editPointsMessage}
                    <div class="mb-4 p-3 bg-green-100 text-green-800 rounded-lg">
                        {editPointsMessage}
                    </div>
                {/if}

                {#if editPointsError}
                    <div class="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
                        {editPointsError}
                    </div>
                {/if}

                <form on:submit|preventDefault={editPointRecord} class="space-y-4">
                    <div>
                        <label for="edit-points-input" class="block text-sm font-medium text-gray-700 mb-1">Points</label>
                        <input
                            id="edit-points-input"
                            type="number"
                            min="0.5"
                            step="0.5"
                            bind:value={editPoints}
                            class="w-full pl-4 pr-8 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                   hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                   transition-all"
                        />
                    </div>

                    <div>
                        <label for="edit-description-input" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea
                            id="edit-description-input"
                            bind:value={editDescription}
                            placeholder="Reason for points"
                            class="w-full pl-4 pr-4 py-2 rounded-lg border border-gray-200 bg-white text-gray-700
                                   hover:border-gray-300 focus:ring-2 focus:ring-secondary focus:border-primary
                                   transition-all"
                            rows="3"
                        ></textarea>
                    </div>

                    <div class="flex justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            on:click={() => showEditModal = false}
                            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg
                                   transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isEditingPoints}
                            class="px-4 py-2 bg-primary hover:bg-secondary text-white font-medium rounded-lg
                                   transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary
                                   disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isEditingPoints ? 'Updating...' : 'Update Points'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    {/if}

    <!-- Delete Confirmation Modal -->
    {#if showDeleteConfirmModal}
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Confirm Deletion</h3>

                <p class="text-gray-700 mb-6">
                    Are you sure you want to delete this point record? This action cannot be undone.
                    <br><br>
                    <span class="font-medium">Details:</span><br>
                    {#if deletingRecord}
                        <span class="text-sm">
                            {deletingRecord.points} points for {deletingRecord.member?.name || 'House'}<br>
                            Description: {deletingRecord.description || 'N/A'}<br>
                            Date: {new Date(deletingRecord.date).toLocaleDateString()}
                        </span>
                    {/if}
                </p>

                <div class="flex justify-end space-x-3">
                    <button
                        type="button"
                        on:click={() => showDeleteConfirmModal = false}
                        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg
                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        on:click={deletePointRecord}
                        disabled={isDeletingPoints}
                        class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg
                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
                               disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isDeletingPoints ? 'Deleting...' : 'Delete Record'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Delete Member Confirmation Modal -->
    {#if showDeleteMemberModal}
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-4">Remove Member</h3>

                <p class="text-gray-700 mb-6">
                    Are you sure you want to remove this member from {userHouse.house} house? This action cannot be undone.
                    <br><br>
                    {#if memberToDelete}
                        <span class="font-medium">Member:</span> {memberToDelete.name}<br>
                        <span class="font-medium">Current Points:</span> {memberToDelete.individual_points}
                        <br><br>
                        <span class="text-red-600 font-medium">Warning:</span> Removing this member will also remove all their point contributions ({memberToDelete.individual_points} points) from the house total.
                    {/if}
                </p>

                <div class="flex justify-end space-x-3">
                    <button
                        type="button"
                        on:click={() => showDeleteMemberModal = false}
                        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg
                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        on:click={deleteMember}
                        disabled={isDeletingMember}
                        class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg
                               transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500
                               disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isDeletingMember ? 'Removing...' : 'Remove Member'}
                    </button>
                </div>
            </div>
        </div>
    {/if}

    {#if showUserHistoryModal}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 relative">
        <button class="absolute top-2 right-3 text-gray-600 text-xl font-bold hover:text-black"
                on:click={() => showUserHistoryModal = false}>×</button>
        <h2 class="text-xl font-semibold mb-4">Point History for {selectedUserName}</h2>
        {#if isFetchingUserHistory}
            <p>Loading...</p>
        {:else if userHistoryError}
            <p class="text-red-600">{userHistoryError}</p>
        {:else if userPointHistory.length === 0}
            <p class="text-gray-600">This user has no point history yet.</p>
        {:else}
            <ul class="space-y-2">
            {#each userPointHistory as record}
                <li class="border p-3 rounded shadow text-sm">
                <div><strong>Date:</strong> {new Date(record.date).toLocaleDateString()}</div>
                <div><strong>Points:</strong> {record.points}</div>
                <div><strong>Description:</strong> {record.description}</div>
                <div><strong>Added by:</strong> {record.added_by.name}</div>
                </li>
            {/each}
            </ul>
        {/if}
        </div>
    </div>
    {/if}

    <!-- Sync Popup Modal -->
    {#if showSyncPopup}
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-pulse">
                <h3 class="text-xl font-semibold text-gray-900 text-center">{syncMessage}</h3>
            </div>
        </div>
    {/if}

</Layout>