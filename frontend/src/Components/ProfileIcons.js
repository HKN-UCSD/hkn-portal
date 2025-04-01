import { userStore } from '../stores.js';

const ImagePath = '/static/profile_icons/';

// User's Level Stuff
let user = null;
let leaderboardData = [];
let level = 0;
let progress = 0;
let pointsToNextLevel = 0;

async function getLeaderboardData() {
    try {
        const response = await fetch('/api/leaderboard/');
        if (response.ok) {
            leaderboardData = await response.json();
        } else {
            console.error("Failed to fetch leaderboard data");
        }
    } catch (error) {
        console.error("Error fetching leaderboard data:", error);
    }
}

async function updateLevelInfo() {
    const totalPoints = getTotalPoints();
    const result = calculateLevel(totalPoints);
    level = result.level;
    progress = result.progress;
    pointsToNextLevel = result.pointsToNextLevel;
}

function getTotalPoints() {
    return leaderboardData?.current_user?.total_points || 0;
}

function calculateLevel(points) {
    let level = 1, requiredPoints = 1, accumulatedPoints = 0;
    while (points >= accumulatedPoints + requiredPoints) {
        accumulatedPoints += requiredPoints;
        level++;
        requiredPoints = Math.min(level, 10);;
    }
    return { level, progress: points - accumulatedPoints, pointsToNextLevel: requiredPoints };
}


new Promise((resolve) => {
    getLeaderboardData();
    updateLevelInfo();
    resolve();
});

/**
 * Populates and returns list of profile icons with their respective paths, status, and requirements.
 * 
 * @param {*} userGroups - List of groups the user belongs to 
 * @returns list of profile icons
 */
export function getUnlockedIcons(userGroups) {
    let ProfileIcons = [
        {
            'id': 1,
            'path': ImagePath + 'UserProfile.png',
            'unlocked': true,
            'requirements': 'None'
        },
        {
            'id': 2,
            'path': ImagePath + 'InducteeProfile.png',
            'unlocked': userGroups.includes("Inductee") || userGroups.includes("Member"),
            'requirements': 'Become an inductee',
        },
        {
            'id': 3,
            'path': ImagePath + 'MemberProfile.png',
            'unlocked': userGroups.includes("Member"),
            'requirements': 'Become a member',
        },
        {
            'id': 4,
            'path': ImagePath + 'OfficerProfile.png',
            'unlocked': userGroups.includes("Officer"),
            'requirements': 'Become an officer',
        },
        {
            'id': 5,
            'path': ImagePath + 'Level5.png',
            'unlocked': level >= 5,
            'requirements': 'Reach level 5',
        },
        {
            'id': 6,
            'path': ImagePath + 'Level8.png',
            'unlocked': level >= 8,
            'requirements': 'Reach level 8',
        }
    ]
    return ProfileIcons;
}