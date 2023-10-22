<script>
    import { navigate } from "svelte-routing";

    async function getFormData() {
        let eventTypeReponse = await fetch('/api/eventtypes/');
        let groupResponse = await fetch('/api/groups/');
        let officerResponse = await fetch('/api/officers/');

        let eventTypes = await eventTypeReponse.json();
        let groups = await groupResponse.json();
        let officers = await officerResponse.json();

        return {
            "eventTypes": eventTypes,
            "groups": groups,
            "officers": officers
        }
    };

    let CSRFToken = document.cookie
                    .split("; ")
                    .find((element) => element.startsWith("csrftoken="))
                    .split("=")[1]

    async function onSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        const eventPhotoInput = form.querySelector('#id_event_photo');
        const eventPhotoFile = eventPhotoInput.files[0];
        
        if (eventPhotoFile) {
            formData.set('event_photo', eventPhotoFile);
        }

        formData.set("csrfmiddlewaretoken", CSRFToken);

        const start_date_in_utc = new Date(formData.get("start_time")).toISOString();
        const end_date_in_utc = new Date(formData.get("end_time")).toISOString();

        if (start_date_in_utc >= end_date_in_utc) {
            alert(`Start Time needs to be before End Time`);
            return false;
        }

        formData.set("start_time", start_date_in_utc);
        formData.set("end_time", end_date_in_utc);

        formData.set("is_draft", true);

        try {
            const response = await fetch(`/api/events/`, {
            method: "POST",
            body: formData
            });

            if (!response.ok) {
                alert(`Unable to create event. Response status ${response.status}`);
            } else {
                alert("Successfully created event");
                navigate('/')
            }
        } catch(error) {
            alert(`Unable to create event. API error ${error}`);
        }
    }
</script>

<svelte:head>
    <title> HKN | Create Event </title>
</svelte:head>

<main>
    {#await getFormData()}
        <p>Loading...</p>
    {:then data}
    <div>
        <form on:submit={onSubmit} enctype="multipart/form-data">
            <tr> 
                <th><label for="id_name">Name:</label></th> 
                <td> <input type="text" name="name" maxlength="255" required id="id_name"> </td> 
            </tr> 
            <tr> 
                <th><label for="id_event_type">Event type:</label></th> 
                <td> 
                    <select name="event_type" required id="id_event_type">
                        <option value="" selected>---------</option> 
                        {#each data.eventTypes as option}
                        <option value={option.name}>{option.name}</option>
                        {/each}
                    </select> 
                </td> 
            </tr> 
            <tr> 
                <th><label for="id_location">Location:</label></th>
                <td> <input type="text" name="location" maxlength="255" id="id_location"> </td> 
            </tr> 
            <tr>
                <th><label for="id_event_photo">Event Photo:</label></th>
                <td> <input type="file" name="event_photo" accept="image/*" id="id_event_photo"> </td>
            </tr>            
            <tr> 
                <th><label for="id_hosts">Hosts:</label></th> 
                <td> 
                    <select name="hosts" required id="id_hosts" multiple> 
                        {#each data.officers as option}
                        <option value={option.user_id}>{option.first_name} {option.last_name}({option.email})</option>
                        {/each}
                    </select> 
                </td> 
            </tr>
            <tr> 
                <th><label for="id_start_time">Start time:</label></th> 
                <td> <input type="datetime-local" name="start_time" id="id_start_time"> </td> 
            </tr> 
            <tr> 
                <th><label for="id_end_time">End time:</label></th> 
                <td> <input type="datetime-local" name="end_time" id="id_end_time"> </td> 
            </tr> 
            <tr> 
                <th><label for="id_points">Points:</label></th> 
                <td> <input type="number" name="points" value="1" step="0.5" required id="id_points"> </td> 
            </tr> 
            <tr> 
                <th><label for="id_view_groups">View groups:</label></th> 
                <td> 
                    <select name="view_groups" id="id_view_groups" multiple> 
                        <option value="1">inductee</option> <!-- TODO: Not too happy about hard coding this list, look for alternatives -->
                        <option value="2">member</option>   <!-- Could use the list of groups from api/groups -->
                        <option value="3">outreach</option> <!-- Open question: how is the int value associated with groups? -->
                        <option value="4">officer</option>
                    </select> 
                </td> 
            </tr> 
            <tr> 
                <th><label for="id_anon_viewable">Visible to guests:</label></th> 
                <td> <input type="checkbox" name="anon_viewable" id="id_anon_viewable"> </td> 
            </tr> 
            <tr> 
                <th><label for="id_description">Description:</label></th> 
                <td> <textarea name="description" cols="40" rows="10" id="id_description"> </textarea> </td> 
            </tr>
            <br /> 
            <input type="submit" value="Save"> 
        </form>
    </div>
    {:catch error}
        <p>Error: {error.message}</p>
    {/await}
</main>

<style>
input[type=text], select {
  width: 100%;
  padding: 12px 20px;
  margin: 8px 0;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
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

label {
    align-content: center;
    vertical-align: middle;
    padding-right: 10px;
}

div {
  border-radius: 5px;
  background-color: #f2f2f2;
  padding: 20px;
}

form {
    grid: 0%;
}
</style>