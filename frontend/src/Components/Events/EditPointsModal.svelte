<script>
	import { createEventDispatcher } from "svelte";
	export let modalUserData;

	let dialog; // HTMLDialogElement
	let pointValue = modalUserData["Points"];
	const dispatch = createEventDispatcher();

	$: if (dialog && modalUserData) {
		dialog.showModal();
	}

	async function onSubmit(event) {
		event.preventDefault();

		const form = event.target;
        const formData = new FormData(form);
		let newPoints = formData.get("points");

		let eventActionPk = modalUserData["Check Off Id"];
        const response = await fetch(`/api/eventactionrecords/${eventActionPk}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.cookie
                    .split("; ")
                    .find((element) => element.startsWith("csrftoken="))
                    .split("=")[1],
            },
            body: JSON.stringify({
                points: newPoints
            }),
        });
		
		dialog.close();
		if (response.status !== 200) {
			alert("Failed to update points.");
			return;
		} else {
			const result = await response.json();
			dispatch("pointsEdited");
			return result;
		}
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
<dialog
	bind:this={dialog}
	class ="max-w-lg w-full rounded-lg border-0 p-0 backdrop:bg-black/30 open:animate-zoom"
>
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div class="p-6" on:click|stopPropagation>
		<h2 class="text-center text-xl font-semibold mb-2">
			Edit Points
		</h2>
		<hr class = "mb-4" />
		<form on:submit={onSubmit} class="flex flex-col gap-4">
			<input type="number" step="0.5" name="points" value={pointValue}>
			<div class="text-center">
				<button
					type="submit"
					class="bg-primary text-white px-4 py-2 rounded-md hover:bg-secondary transition-colors"
				>
					Submit
				</button>
			</div>
		</form>
	</div>
</dialog>