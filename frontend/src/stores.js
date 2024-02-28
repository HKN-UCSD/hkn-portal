import { readable } from "svelte/store";

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