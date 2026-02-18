import { readable, writable } from "svelte/store";

export let userStore = writable(null);

export async function fetchUser() {
    try {
        const response = await fetch("/api/profile/self/", {
            credentials: "include"
        });     

        if (response.status === 403 || response.status === 401) {
            // Not authenticated → redirect to Django login
            const returnUrl = encodeURIComponent(window.location.href);
            window.location.href = `/accounts/login/?next=${returnUrl}`;
            return;
        }

        if (!response.ok) throw new Error('Failed to fetch user data');

        const userData = await response.json();
        userStore.set(userData);
    } catch (error) {
        console.error('Error fetching user data:', error);
        // On fetch error, also redirect to login
        const returnUrl = encodeURIComponent(window.location.href);
        window.location.href = `/accounts/login/?next=${returnUrl}`;
    }
}

// Populate userStore when app starts
fetchUser();

export const adminStatus = readable(
    null,
    (set) => {
        async function getAdminStatus() {
            if (sessionStorage.getItem('adminStatus')) {
                set(sessionStorage.getItem('adminStatus') === 'true');
                return; 
            }
            let response = await fetch(`/api/permissions/`, {
                credentials: "include"
            });
            if (response.status === 200) {
                let output = await response.json();
                let admin = output.is_admin;
                sessionStorage.setItem('adminStatus', admin);
                set(admin);
            } else {
                console.error('Failed to fetch user status');
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
                let response = await fetch(`/api/permissions/`, {
                    credentials: "include"
                });
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
        const response = await fetch(`/api/profile/self/`, {
            credentials: "include"
        });
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