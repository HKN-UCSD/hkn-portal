import { writable } from 'svelte/store'

export const eventstore = writable();
export const eventview = writable("list");