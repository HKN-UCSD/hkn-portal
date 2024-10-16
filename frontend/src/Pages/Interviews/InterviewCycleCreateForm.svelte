<script>
    import * as utils from "../../utils"
    let csrftoken = utils.getCsrfToken();
</script>

<form action="/api/interviewcycles" method="post" id="interviewcyclecreateform">
    <!-- Induction Class selection -->
    <input type="text" name="induction_class" />
    <!-- start date selection -->
    <input type="date" name="start_date"/>
    <!-- end date selection -->
    <input type="date" name="end_date"/>
    <!-- start time selection -->
    <input type="time" name="start_time"/>
    <!-- end time selection -->
    <input type="time" name="end_time"/>
    <!-- Open weekends checkbox -->
    <input type="hidden" name="csrfmiddlewaretoken" value={csrftoken} />
    <button type="submit">Create</button>
</form>

