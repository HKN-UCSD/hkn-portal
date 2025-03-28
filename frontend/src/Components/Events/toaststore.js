import { writable } from 'svelte/store';

export const toastMessage = writable('');
export const showToast = writable(false);

export function triggerToast(message, duration = 4000) {
    toastMessage.set(message);
    showToast.set(true);
    setTimeout(() => {
        showToast.set(false);
        toastMessage.set('');
    }, duration);
}