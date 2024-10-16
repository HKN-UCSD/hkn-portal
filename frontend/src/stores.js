import { readable } from "svelte/store";
import { writable } from 'svelte/store';

const states = {
    SUCCESS: 0,
    FAILURE: 1,
    PENDING: 2, 
};

export let userStore = readable(
    states.PENDING,
    (set) => {
        let response = fetch(`/api/users/self/`).then((value) => {
            return value.json();
        }).then((value) => {
            set(value);
        }).catch((reason) => {
            set(states.FAILURE);
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
