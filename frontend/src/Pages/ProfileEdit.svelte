<script>
    import { navigate } from "svelte-routing";
    import Layout from "../Layout.svelte";
    import { get_custom_elements_slots } from "svelte/internal";
    

    let user_groups = []
    let user_data = null;
    let first_name = null;

    let other_major = true;
    let other_major_value = "";
    let other_degree = true;
    let other_degree_value = "";

    function checkMajor(major, currOption) {
        if (currOption == major) {
            other_major = false;
            return true;
        } else if ((currOption == "Other") && other_major) {
            other_major_value = major;
            return true;
        } else {
            return false; 
        }
    }

    function checkDegree(degree, currOption) {
        if (currOption == degree) {
            other_degree = false;
            return true;            
        } else if ((currOption == "Other") && other_degree) {
            other_degree_value = degree;
            return true;
        } else {
            return false;
        }
    }

    async function getProfileData() {
        try {
            const response = await fetch(`/api/profile/self/`);
            if (response.ok) {
                user_data = await response.json();
            } else {
                console.error("Failed to fetch self data");
            }
        } catch (error) {
            console.error("Error fetching user data", error);
        }
        for (let group of ["Inductee", "Member", "Outreach Student", "Officer"]) {
            if (user_data[group]) {
                user_groups.push(group);
            }
        }

        let user = await (await(fetch(`/api/profile/self/`))).json()
        first_name = user.first_name
        let majors = await (await fetch(`/api/majors/`)).json()
        let degrees = await (await fetch(`/api/degreelevel/`)).json()

        let formData = {
            majors: majors,
            degrees: degrees,
        }

        formData["user"] = user
        
        return formData;
    }

    let CSRFToken = document.cookie
        .split("; ")
        .find((element) => element.startsWith("csrftoken="))
        .split("=")[1];

    async function onSubmit(event) {
        event.preventDefault();

        const form = event.target;

        // sort form data
        // customUser
        //    preferred_name, grad_year
        // inductee/member
        //    major, degree
        // outreach
        //    car

        const formData = new FormData(form);

        formData.set("csrfmiddlewaretoken", CSRFToken);

        if (formData.get("preferred_name") == "") {
            formData.set("preferred_name", first_name)
        }

        if (formData.get("major") == "Other") {
            formData.set("major", formData.get("other_major"))
        }
        if (formData.get("degree") == "Other") {
            formData.set("degree", formData.get("other_degree"))
        }

        const response = await fetch(`/api/profile/edit/`, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": CSRFToken,
            },
        });
        if (!response.ok) {
            alert(
                `Unable to save changes. Response status ${response.status}`
            );
        } else {
            alert("Changes saved");
            navigate("/profile/self")
        }
    }
</script>

<Layout>
<main>
    <title>
        HKN | Edit Profile
    </title>
    <h1 style="margin-left: 15px">Edit Profile</h1>
    {#await getProfileData()}
        <p>Loading...</p>
    {:then data}
        <div>
            <form on:submit={onSubmit} id="edit_form">
                <div class="container">
                    <h2>{data.user.first_name} 
                        (<input
                            type="text"
                            name="preferred_name"
                            maxlength="255"
                            id="id_preferred_name"
                            value={data.user.preferred_name === data.user.first_name ? "" : data.user.preferred_name}
                            placeholder="Preferred Name"
                        />)
                        {data.user.last_name}
                    </h2>
                    {#each user_groups as group}
                        {#if group == "Inductee" || group == "Member"}
                        <table>
                            <tr>
                                <td><h3>Email:</h3></td>
                                <td><p>{data.user.email}</p></td>
                                <td><h3>Major:</h3></td>
                                <td>
                                    <select name="major" required id="id_major">
                                        {#each data.majors as option}
                                            <option 
                                                value={option.name}
                                                selected={checkMajor(data.user[group].major, option.name)}>{option.name}
                                            </option>
                                        {/each}
                                    </select>
                                    <input
                                        type="text"
                                        name="other_major"
                                        maxlength="255"
                                        id="id_other_major"
                                        value={other_major_value}
                                        placeholder="Other Major"
                                    />
                                    <script>
                                        console.log("running script");
                                        var otherMajorInput = document.getElementById("id_other_major");
                                        var majorInput = document.getElementById("id_major");

                                        if (majorInput.value == "Other") {
                                            otherMajorInput.style.display = "block";
                                        } else {    
                                            otherMajorInput.style.display = "none";
                                        }
                            
                                        var majorSelect = document.getElementById("id_major");
                                        majorSelect.addEventListener("change", function() {
                                            if (majorSelect.value == "Other") {
                                                otherMajorInput.style.display = "block";
                                                otherMajorInput.required = true;
                                            } else {
                                                otherMajorInput.style.display = "none";
                                                otherMajorInput.required = false;
                                            }
                                        });
                                    </script>
                                </td>
                            </tr>
                            <tr>
                                <td><h3>Degree: </h3></td>
                                <td>
                                    <select name="degree" required id="id_degree">
                                        {#each data.degrees as option}
                                            <option 
                                                value={option.name}
                                                selected={checkDegree(data.user[group].degree, option.name)}>{option.name}
                                            </option>
                                        {/each}
                                    </select>
                                    <input
                                        type="text"
                                        name="other_degree"
                                        maxlength="255"
                                        id="id_other_degree"
                                        value={other_degree_value}
                                        placeholder="Other Degree"
                                    />
                                    <script>
                                        console.log("running script");
                                        var otherDegreeInput = document.getElementById("id_other_degree");
                                        var degreeInput = document.getElementById("id_degree");

                                        if (degreeInput.value == "Other") {
                                            otherDegreeInput.style.display = "block";
                                        } else {
                                            otherDegreeInput.style.display = "none";
                                        }
                            
                                        var degreeSelect = document.getElementById("id_degree");
                                        degreeSelect.addEventListener("change", function() {
                                            if (degreeSelect.value == "Other") {
                                                otherDegreeInput.style.display = "block";
                                                otherDegreeInput.required = true;
                                            } else {
                                                otherDegreeInput.style.display = "none";
                                                otherDegreeInput.required = false;
                                            }
                                        });
                                    </script>
                                </td>
                                
                                <td><h3>Graduation Year: </h3></td>
                                <td>
                                    <select name="grad_year" required id="id_grad_year">
                                        <!-- get current year and plus minus 5 years -->
                                        {#each Array.from({length: 11}, (_, i) => i + new Date().getFullYear() - 5).reverse() as year}
                                            <option 
                                                value={year}
                                                selected={data.user[group].grad_year && data.user[group].grad_year == year}>{year}
                                            </option>
                                        {/each}                                        
                                    </select>
                                </td>
                            </tr>
                            {#if group == "Member"}
                                <tr>
                                    <td><h3>Induction Class:</h3></td>
                                    <td><p>{data.user.induction_class}</p></td>
                                </tr>
                            {/if}
                        </table>
                        {/if}
                    {/each}
                </div>
                {#each user_groups as group}
                    {#if group != "Member"}
                    <div class="container">
                        <h2>{group}</h2>
                        <!-- Display induction information -->
                        {#if group == "Inductee"}
                            <table>
                                <tr>
                                <td><h3>Induction Class:</h3></td>
                                <td><p>{data.user.induction_class.name}</p></td>
                                </tr>
                                <tr>
                                <td><h3>Professional</h3></td>
                                <td><p>{data.user[group].professional_points} / 1</p></td>
                                <td><h3>Social</h3></td>
                                <td><p>{data.user[group].social_points} / 2</p></td>
                                <td><h3>Technical</h3></td>
                                <td><p>{data.user[group].technical_points} / 1</p></td>
                                </tr>
                                <tr>
                                <td><h3>Outreach</h3></td>
                                <td><p>{data.user[group].outreach_points} / 1</p></td>
                                <td><h3>Mentorship</h3></td>
                                <td><p>{data.user[group].mentorship_points} / 1</p></td>
                                <td><h3>General</h3></td>
                                <td><p>{data.user[group].general_points}</p></td>
                                </tr>
                                <tr>
                                <td><h3>Total</h3></td>
                                <td><p>{data.user[group].total_points} / 10</p></td>
                                </tr>
                            </table>

                        <!-- Display outreach student information -->
                        {:else if group == "Outreach Student"}
                            <table id="change-in-mobile">
                                <tr>
                                <td><h3>198 Course:</h3></td>
                                <td><p>{data.user[group].outreach_course}</p></td>
                                <td><h3>Quarter:</h3></td>
                                <td><p>{data.user[group].quarter}</p></td>
                                <td><h3>Hours:</h3></td>
                                <td><p>{data.user[group].hours}</p></td>
                                <td><h3>Car:</h3></td>
                                <td>
                                    <select name="car" required id="id_car">
                                        <option value="Yes" selected={data.user[group].car == "Yes"}>Yes</option>
                                        <option value="No" selected={data.user[group].car == "No"}>No</option>
                                    </select>
                                </td>
                                </tr>
                            </table>

                        <!-- Display officer information -->
                        {:else if group == "Officer"}
                            <table>
                                <tr>
                                <td><h3>Position:</h3></td>
                                <td><p>{data.user[group].position}</p></td>
                                </tr>
                                <!-- Add house information once house system is implemented-->
                            </table>
                        {/if}
                    </div>
                    {/if}
                {/each}
                <input type="submit" value="Save"/>
            </form>
        </div>
    {/await}
</main>
</Layout>

<style>
    .container {
       padding: 10px 10px;
       border-radius: 5px;
       box-shadow: 0px 1px 2px 1px lightgray;
       grid-area: c;
       margin: 10px;
       background-color: #f5f5f5;
       width: 95%;
    }

    form input[type="submit"] {
        margin: 10px;
        color: white;
        border-radius: 0.25em;
        padding: 0.4em 0.65em;
        background-color: var(--fc-button-bg-color);
        border: none;
        outline: none;
    }
 
    h2 {
       margin: 0px 10px 0px 0px;
       
    }
 
    h3 {
       margin: 0px 10px 0px 0px;
       min-width: 20px;
    }
 
    p {
       margin: 0px 25px 0px 0px;
    }
 
    table {
       text-align: left;
       table-layout: auto;
       max-width: 100%;
    }
 
    td {
       padding: 5px 20px 5px 0px;
    }
 </style>