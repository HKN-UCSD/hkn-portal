<script>
    import { onMount, onDestroy } from 'svelte';
    export let show;
    export let profileIcon;

    export let onSave = () => {};
    export let onClose = () => {};
    let userInfo;

    onMount(async () => {
        const handleKeydown = (event) => {
            if (event.key === "Escape") {
                onClose();
            }
        }
        document.addEventListener("keydown", handleKeydown);
    });

    let editedProfileIcon = profileIcon;

    function saveAndClose() {
        onSave({ profileIcon: editedProfileIcon });
        onClose();
    };

    function onCancel() {
        editedProfileIcon = profileIcon;
        onClose();
    }

  </script>