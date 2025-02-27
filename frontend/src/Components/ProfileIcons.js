const ImagePath = '/static/';

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
            'unlocked': userGroups.includes("Inductee"),
            'requirements': 'Become an inductee',
        },
        {
            'id': 3,
            'path': ImagePath + 'MemberProfile.png',
            'unlocked': userGroups.includes("Member"),
            'requirements': 'Become a member',
        },
    ]
    return ProfileIcons;
}