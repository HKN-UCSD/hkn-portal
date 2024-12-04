import { readable } from "svelte/store";
import { writable } from 'svelte/store';


export let userStore = readable(
    null,
    (set) => {
        // fetch a thing
        let response = fetch(`/api/users/self/`).then((value) => {
            return value.json();
        }).then((value) => {
            set(value);
        });

        return () => null
    }
)

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