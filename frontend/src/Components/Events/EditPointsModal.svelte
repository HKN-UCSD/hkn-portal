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
>
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div on:click|stopPropagation>
		<h2 class="align_center">
			Edit Points
		</h2>
		<hr />
		<form on:submit={onSubmit}>
			<input type="number" step="0.5" name="points" value={pointValue}>
		<hr />
		<div class="align_center">
			<input type="submit" value="Submit"> 
		</div>
		</form>
	</div>
</dialog>

<style>
	dialog {
		max-width: 32em;
		border-radius: 0.2em;
		border: none;
		padding: 0;
	}
	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}
	dialog > div {
		padding: 1em;
	}
	dialog[open] {
		animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	@keyframes zoom {
		from {
			transform: scale(0.95);
		}
		to {
			transform: scale(1);
		}
	}
	dialog[open]::backdrop {
		animation: fade 0.2s ease-out;
	}
	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	.align_center{
		text-align: center;
	}

	form input[type="submit"] {
		color: white;
		/* background-color: #f4f4f4; */
		border-radius: 0.25em;
		padding: 0.4em 0.65em;
		background-color: var(--fc-button-bg-color);
		border: none;
		outline: none;
	}
</style>
