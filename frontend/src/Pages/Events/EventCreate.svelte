<script>
    import { navigate } from "svelte-routing";
    import { getFormData } from "../../Components/Events/eventutils";
    import Layout from "../../Layout.svelte";

    export let idOfEventToEdit = undefined;

    let CSRFToken = document.cookie
        .split("; ")
        .find((element) => element.startsWith("csrftoken="))
        .split("=")[1];

    async function onSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        formData.set("csrfmiddlewaretoken", CSRFToken);

        const start_date_in_utc = new Date(
            formData.get("start_time")
        ).toISOString();
        const end_date_in_utc = new Date(
            formData.get("end_time")
        ).toISOString();

        if (start_date_in_utc >= end_date_in_utc) {
            alert(`Start Time needs to be before End Time`);
            return false;
        }

        formData.set("start_time", start_date_in_utc);
        formData.set("end_time", end_date_in_utc);

        formData.set("is_draft", !formData.get("is_draft"));

        try {
            if (idOfEventToEdit == undefined) {
                const response =
                        await fetch(`/api/events/`, {
                              method: "POST",
                              body: formData,
                              headers: {
                                  "X-CSRFToken": CSRFToken,
                              },
                          })

                if (!response.ok) {
                    alert(
                        `Unable to create event. Response status ${response.status}`
                    );
                } else {
                    alert("Successfully created event");
                    navigate("/");
                }
            } else {
                const response = await fetch(`/api/events/${idOfEventToEdit}/`, {
                              method: "PUT",
                              body: formData,
                              headers: {
                                  "X-CSRFToken": CSRFToken,
                              },
                          });
                if (!response.ok) {
                    alert(
                        `Unable to edit event. Response status ${response.status}`
                    );
                } else {
                    navigate(`/events/${idOfEventToEdit}`);
                }
            }
        } catch (error) {
            alert(`Unable to create event. API error ${error}`);
        }
    }
</script>


<svelte:head>
    <title>HKN | {idOfEventToEdit == undefined ? "Create" : "Edit"} Event</title>
</svelte:head>
<Layout>
    <main>
        <title>
            HKN | {idOfEventToEdit == undefined ? "Create" : "Edit"} Event
        </title>
        {#await getFormData(idOfEventToEdit)}
            <p>Loading...</p>
        {:then data}
            <div>
                <form on:submit={onSubmit}>
                    <tr>
                        <th><label for="id_name">Name:</label></th>
                        <td>
                            <input
                                type="text"
                                name="name"
                                maxlength="255"
                                required
                                id="id_name"
                                value={data.eventToEdit.name || ""}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_event_type">Event type:</label></th>
                        <td>
                            <select name="event_type" required id="id_event_type">
                                <option value="" selected>---------</option>
                                {#each data.eventTypes as option}
                                    <option
                                        value={option.name}
                                        selected={data.eventToEdit.event_type &&
                                            data.eventToEdit.event_type ==
                                                option.name}>{option.name}</option
                                    >
                                {/each}
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_location">Location:</label></th>
                        <td>
                            <input
                                type="text"
                                name="location"
                                maxlength="255"
                                id="id_location"
                                value={data.eventToEdit.location || ""}
                            />
                        </td>
                    </tr> 
                    <tr>
                        <th><label for="id_embed_code">Embed Code:</label></th>
                        <td>
                            <input
                                type="text"
                                name="embed_code"
                                id="id_embed_code"
                                placeholder="Paste the Canva embed code here..."
                                value={data.eventToEdit.embed_code || ""}
                            />
                        </td>
                    </tr>          
                    <tr>
                        <th><label for="id_hosts">Hosts:</label></th>
                        <td>
                            <select name="hosts" id="id_hosts" multiple>
                                {#each data.officers as option}
                                    <option
                                        value={option.user_id}
                                        selected={data.eventToEdit.hosts &&
                                            data.eventToEdit.hosts.includes(
                                                option.user_id
                                            )}
                                        >{option.first_name}
                                        {option.last_name}({option.email})</option
                                    >
                                {/each}
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_start_time">Start time:</label></th>
                        <td>
                            <input
                                type="datetime-local"
                                name="start_time"
                                id="id_start_time"
                                value={data.eventToEdit.start_time}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_end_time">End time:</label></th>
                        <td>
                            <input
                                type="datetime-local"
                                name="end_time"
                                id="id_end_time"
                                value={data.eventToEdit.end_time}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_points">Points:</label></th>
                        <td>
                            <input
                                type="number"
                                name="points"
                                value={data.eventToEdit.points
                                    ? data.eventToEdit.points
                                    : 1}
                                step="0.5"
                                required
                                id="id_points"
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_view_groups">View groups:</label></th>
                        <td>
                            <select name="view_groups" id="id_view_groups" multiple>
                                <option
                                    value="1"
                                    selected={data.eventToEdit.view_groups &&
                                        data.eventToEdit.view_groups.includes(1)}
                                    >inductee</option
                                >
                                <!-- TODO: Not too happy about hard coding this list, look for alternatives -->
                                <option
                                    value="2"
                                    selected={data.eventToEdit.view_groups &&
                                        data.eventToEdit.view_groups.includes(2)}
                                    >member</option
                                >
                                <!-- Could use the list of groups from api/groups -->
                                <option
                                    value="3"
                                    selected={data.eventToEdit.view_groups &&
                                        data.eventToEdit.view_groups.includes(3)}
                                    >outreach</option
                                >
                                <!-- Open question: how is the int value associated with groups? -->
                                <option
                                    value="4"
                                    selected={data.eventToEdit.view_groups &&
                                        data.eventToEdit.view_groups.includes(4)}
                                    >officer</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_anon_viewable">Visible to guests:</label></th>
                        <td>
                            <input
                                type="checkbox"
                                name="anon_viewable"
                                id="id_anon_viewable"
                                checked={data.eventToEdit.anon_viewable !== undefined ? data.eventToEdit.anon_viewable : false}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_is_time_restricted">Time restricted:</label></th>
                        <td>
                            <input
                                type="checkbox"
                                name="is_time_restricted"
                                id="id_is_time_restricted"
                                checked={data.eventToEdit.is_time_restricted !== undefined ? data.eventToEdit.is_time_restricted : true}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_is_draft">Mark event as ready:</label></th>
                        <td>
                            <input
                                type="checkbox"
                                name="is_draft"
                                id="id_is_draft"
                                checked={data.eventToEdit.is_draft !== undefined ? !data.eventToEdit.is_draft : false}
                            />
                        </td>
                    </tr>
                    <tr>
                        <th><label for="id_description">Description:</label></th>
                        <td>
                            <textarea
                                name="description"
                                cols="40"
                                rows="10"
                                id="id_description"
                                value={data.eventToEdit.description}
                            />
                        </td>
                    </tr>
                    <br />
                    <input type="submit" value="Save" />
                </form>
            </div>
        {:catch error}
            <p>Error: {error.message}</p>
        {/await}
    </main>
</Layout>
<style>
    input[type="text"],
    select {
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