export class InterviewCycleNonexistError extends Error{
    constructor(message) {
        super(message);
        this.name = "InterviewCycleNonexistError";
    }
}


export class AvailabilityNotCreatedError extends Error{
    constructor(message, inductionClass) {
        super(message);
        this.name = "AvailabilityNotCreatedError";
        this.inductionClass = inductionClass;
    }
}

