import Page1 from './pages/test_page1/Page1.svelte';
import Page2 from './pages/test_page2/Page2.svelte';
import App from './App.svelte';

function get_page(page) {
	return new page({
		target: document.body,
		props: {
			name: 'World',
			page: window.location.pathname
		}
	})
}

function page_selector() {
	switch (window.location.pathname){
		case '/page1' :
			return get_page(Page1);
		case '/page2' :
			return get_page(Page2);
		default:
			return get_page(App);
	}
}

const app = page_selector()

export default app;