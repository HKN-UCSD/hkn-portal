""" Model definitions for interview-related data.

This module contains class definitions for models that structure
interview-related data. This includes data describing an interview cycle's
start and end dates, the hours on each of those dates that interviews will
be held, whether interviews will be held on weekends, and information about
each student's availability for a given interview cycle.


Typical usage example:

    Bruh

"""
from datetime import date, datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import BinaryField, BooleanField, DateField, TimeField
from .users import CustomUser, InductionClass


class InterviewCycle(models.Model):
    """
    Implementation of the model of an interview cycle. An interview cycle consists of
    a range of days with set hours each day for interviewing, as well as the set of
    availabilities any interviewing users have for this range of time.

    """

    start_date = DateField()
    end_date = DateField()
    open_weekends = BooleanField()
    start_time = TimeField()
    end_time = TimeField()
    induction_class = models.OneToOneField(
        to=InductionClass, on_delete=CASCADE, related_name="interview_cycle"
    )
    # availabilities = set of InterviewAvailabilities

    def clean(self):
        """
        Validation for InterviewCycle objects. Does not return any value; only raises
        an error if the object is invalid.
        - Checks that the end date is after the start day.
        - Checks that the start time is on a 15-minute interval
        - Checks that the end time is on a 15-minute interval
        """
        # Check that the end date is after the start day.
        daterange: timedelta = self.end_date - self.start_date
        num_days = daterange.days
        errormsgs = []
        if num_days <= 0:
            errormsgs.append("End date is before start date")
        if self.start_time >= self.end_time:
            errormsgs.append("End time is before start time")
        # Check that the start time is on a 15-minute interval
        if self.start_time.second != 0 or self.start_time.minute % 15 != 0:
            errormsgs.append("Start time is not on a 15-minute division")
        if self.end_time.second != 0 or self.end_time.minute % 15 != 0:
            errormsgs.append("End time is not on a 15-minute division")
        if self.num_slots <= 0:
            errormsgs.append("No timeslots would be available in this interview cycle")
        if errormsgs:
            raise ValidationError(";\n".join(errormsgs))

    @property
    def num_slots(self):
        daterange: timedelta = self.end_date - self.start_date
        num_days = daterange.days
        if not self.open_weekends:
            wd = self.start_date.weekday()
            extra_days = num_days % 7
            num_weeks = num_days // 7
            num_weekends = (
                2 * num_weeks
                + (min(2, wd + extra_days - 5) if wd < 6 else min(1, extra_days))
            )
            num_days -= num_weekends

        arbitrary_time = date.today()
        timerange: timedelta = datetime.combine(arbitrary_time, self.end_time) - datetime.combine(arbitrary_time, self.start_time)
        return (num_days * timerange.seconds) // 900


class InterviewAvailability(models.Model):
    """
    Implementation of the model of a user's interview availability. Consists of a
    user to which this availability pertains, the interview
    cycle that this availability pertains to, and a
    set of bytes indicating which timeslots the user is available in
    """

    slots = BinaryField()  # TODO: Document which bit pertains to which slot availability
    user = models.OneToOneField(
        to=CustomUser, on_delete=CASCADE, related_name="availability"
    )
    interview_cycle = models.ForeignKey(
        to=InterviewCycle, on_delete=CASCADE, related_name="availabilities"
    )

    def clean(self):
        """
        Validation for InterviewAvailability objects. Does not return any value;
        only raises an error if the object is invalid.
        - Checks if the number of bits in `slots` is the same as the number of
          slots available in `interview_cycle`. In other words, checks if the
          number of slot availabilities indicated by the `slots` encoding
          fits within the the number of slots actually available during the given
          interview cycle.
        """

        # Check if the number of bits in `slots` is the same as 
        if 8 * len(self.slots) != self.interview_cycle.num_slots:
            raise ValidationError(
                "The number of slots given in this availability is not equivalent "
                "to the number of slots in its interview cycle"
            )
