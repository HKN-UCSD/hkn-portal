const ImagePath = '/static/profile_icons/';

/**
 * Populates and returns list of profile icons with their respective paths, status, and requirements.
 * 
 * @param {*} userGroups - List of groups the user belongs to 
 * @returns list of profile icons
 */
export function getUnlockedIcons(userGroups, level) {
    let ProfileIcons = [
        {
            'id': 1,
            'path': ImagePath + 'User.png',
            'unlocked': true,
            'requirements': 'None'
        },
        {
            'id': 2,
            'path': ImagePath + 'Inductee.png',
            'unlocked': userGroups.includes("Inductee") || userGroups.includes("Member"),
            'requirements': 'Become an inductee',
        },
        {
            'id': 3,
            'path': ImagePath + 'Member.png',
            'unlocked': userGroups.includes("Member"),
            'requirements': 'Become a member',
        },
        {
            'id': 4,
            'path': ImagePath + 'Officer.png',
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
        },
        {
            'id': 7,
            'path': ImagePath + 'Level10.png',
            'unlocked': level >= 10,
            'requirements': 'Reach level 10',
        }
    ]
    return ProfileIcons;
}