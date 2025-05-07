import { readable, writable } from "svelte/store";

export let userStore = writable(null);

export async function fetchUser() {
    console.log('Fetching user data...');
    try {
        const response = await fetch(`/api/profile/self/`);
        if (!response.ok) throw new Error('Failed to fetch user data');

        const userData = await response.json();
        userStore.set(userData);
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
}

// Populate userStore when app starts
fetchUser();

// export let userStore = readable(
//     null,
//     (set) => {
//         let response = fetch(`/api/users/self/`).then((value) => {
//             return value.json();
//         }).then((value) => {
//             set(value);
//         });

//         return () => null
//     }
// )

export const adminStatus = readable(
    null,
    (set) => {
        async function getAdminStatus() {
            if (sessionStorage.getItem('adminStatus')) {
                set(sessionStorage.getItem('adminStatus') === 'true');
                return; 
            }
            let response = await fetch(`/api/permissions/`);
            if (response.status === 200) {
                let output = await response.json();
                let admin = output.is_admin;
                sessionStorage.setItem('adminStatus', admin);
                set(admin);
            } else {
                console.error('Failed to fetch user status:', error);
                set(null);
            }

        }
        getAdminStatus();
    }
);

export const memberStatus = readable(
    false,
    (set) => {
        async function getMemberStatus() {
            if (sessionStorage.getItem('memberStatus')) {
                set(sessionStorage.getItem('memberStatus') === 'true');
                return; 
            }
            try{
                let response = await fetch(`/api/permissions/`);
                if (response.status === 200) {
                    let output = await response.json();
                    let member = output.is_member;
                    sessionStorage.setItem('memberStatus', member);
                    set(member);
                } else {
                    console.error('Failed to fetch user status:', response.statusText);
                    set(false);
                }
            } catch (error) {
                console.error('Error fetching user status:', error);
                set(false);
            }
        }
        getMemberStatus();
    }
);

export const interviewEligibility = readable(
    null,
    (set) => {
        async function getInterviewEligibility() {
            if (sessionStorage.getItem('interviewEligible')) {
                set(sessionStorage.getItem('interviewEligible') === 'true');
                return; 
            }
            let response = await fetch(`/api/profile/sel/`);
            if (response.status === 200) {
                let output = await response.json();
                if (output.hasOwnProperty('Inductee')) {
                    let eligibility = output['Inductee']['total_points'] >= 6;
                    sessionStorage.setItem('interviewEligible', eligibility);
                    set(eligibility);
                }
                set(null);
                
            } else {
                console.error('Failed to fetch interview eligibility:', error);
                set(null);
            }
        }
        getInterviewEligibility();
    }
);