from datetime import date, time
from django.core.exceptions import ValidationError
from django.test import TestCase
from myapp.api.models.interviews import InterviewCycle
from myapp.api.models.users import InductionClass
from myapp.api.serializers import (
    BaseInterviewCycleSerializer,
    BaseInterviewAvailabilitySerializer,
    OfficerInterviewCycleSerializer,
)


class TestInterviewCycleSerializer(TestCase):
    def setUp(self) -> None:
        self.induction_class = InductionClass(
            name="Beta",
            start_date=date(2024, 10, 1),
            end_date=date(2024, 12, 2),
            academic_year=2024,
        )
        self.induction_class.save()

        self.cycles = [
            {
                "start_date": date(2024, 10, 6),
                "end_date": date(2024, 10, 7),
                "start_time": time(hour=10),
                "end_time": time(hour=22),
                "open_weekends": False,
                "induction_class": self.induction_class,
            }
        ]

        self.invalid_cycles = [
            {
                "start_date": date(2024, 10, 6),
                "end_date": date(2024, 10, 5),
                "start_time": time(hour=10),
                "end_time": time(hour=22),
                "open_weekends": False,
                "induction_class": self.induction_class.pk,
            }
        ]

    def test_interview_cycle_serialize_success(self):
        serializer = BaseInterviewCycleSerializer(data=self.cycles[0])
        officer_serializer = OfficerInterviewCycleSerializer(data=self.cycles[0])
        serializer.is_valid()
        officer_serializer.is_valid()

    def test_interview_cycle_serializer_invalid(self):
        serializer = BaseInterviewCycleSerializer(data=self.invalid_cycles[0])
        validity = serializer.is_valid()
        self.assertFalse(validity)
