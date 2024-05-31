<script>
    export let placeholder;
    export let options;
    export let name;
    export let id;
    let availableOptions = Array.from(options);
    let filteredOptions = Array.from(availableOptions);
    let selectedOptions = [];
    let searchText; // bound
    let availableBlock; // bound

    let realField;

    // let updateQueued = false;
    // let updateLock = false;

    // TODO: optimize everything. 
    // maintain that both the available list and the selected list are ordered somehow
    // use binary search to look for everything or use some other data structure
    // that makes shifting elements between these two sets quick and searching
    // for them quick.
    const updateDropdown = () => {
        filteredOptions = availableOptions.filter((word) => searchText == undefined || word.startsWith(searchText)).toSorted();
    }
    const selectOption = (option) => {
        let selectedOption = availableOptions.splice(availableOptions.indexOf(option), 1);
        selectedOptions = selectedOptions.concat(selectedOption).toSorted();
        for (option of realField.options) {
            if (option.value == selectedOption) {
                option.selected = true;
                break;
            }
        }
        searchText = "";
        hideAvailable();
        updateDropdown();
    }
    const deleteOption = (option) => {
        let availableOption = selectedOptions.splice(selectedOptions.indexOf(option), 1);
        selectedOptions = selectedOptions.toSorted();
        availableOptions = availableOptions.concat(availableOption);
        for (option of realField.options) {
            if (option.value == availableOption) {
                option.selected = false;
                break;
            }
        }
        updateDropdown();
    }
    const showAvailable = () => {
        availableBlock.hidden = false;
    }
    const hideAvailable = () => {
        availableBlock.hidden = true;
    }
</script>

<div class="dropdown">
    <input form="" class="searchinput" type="text" placeholder={placeholder} autocomplete="off" on:keyup={() => {showAvailable(); updateDropdown();}} bind:value={searchText} on:focus={() => showAvailable()} on:blur={() => hideAvailable()}>
    <select name={name} id={id} bind:this={realField} multiple hidden>
        {#each options as option}
            <option value={option}></option>
        {/each}
    </select>
    <div class="available" bind:this={availableBlock} hidden>
    {#each filteredOptions as option}
        <button type="button" on:mousedown={(ev) => { ev.preventDefault(); }} on:click={() => selectOption(option)}>{option}</button>
    {/each}
    </div>
    <div class="selected">
    {#each selectedOptions as selectedOption}
        <button type="button" on:click={() => deleteOption(selectedOption)}>X {selectedOption}</button>
    {/each}
    </div>
</div>

<style>
    div.dropdown {
        width: 300px;
    }

    div.dropdown input.searchinput {
        width: 100%;
    }

    div.available {
        width: 300px;
        max-height: 200px;
        overflow-y: scroll;
        overflow-x: clip;
        position: absolute;
        background-color: white;
    }
    button {
        margin: 5px;
    }
    div.selected button {
        text-align: center;
        vertical-align: middle;
    }
</style>
