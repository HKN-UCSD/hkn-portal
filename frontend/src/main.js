import App from './App.svelte';
import "../main.css"
import { refreshInterviewEligibility} from "./stores.js";

async function init() {
    await Promise.all([
        refreshInterviewEligibility(),     
    ]);

    new App({
        target: document.body,
    });
}

init();
