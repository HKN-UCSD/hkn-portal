import { readable, writable } from "svelte/store";

export let userStore = writable(null);

export async function fetchUser() {
    try {
        const response = await fetch("/api/profile/self/", {
            credentials: "include"
        });     

        if (response.status === 403) {
            // CSRF or session expired → force login
            window.location.href = "/accounts/login/?next=" + window.location.pathname;
            return;
        }

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

export const interviewEligibility = writable(null);
export async function refreshInterviewEligibility() {
    try {
        const response = await fetch(`/api/profile/self/`);
        if (!response.ok) {
            interviewEligibility.set(null);
            return;
        }

        const data = await response.json();

        const points = data?.Inductee?.total_points ?? 0;
        const eligible = points >= 5;

        interviewEligibility.set(eligible);
        sessionStorage.setItem("interviewEligible", eligible);
    } catch (err) {
        console.error("Error fetching eligibility:", err);
        interviewEligibility.set(null);
    }
}

refreshInterviewEligibility();