from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase

from myapp.api.models.interviews import InterviewAvailability, InterviewCycle
from myapp.api.models.users import CustomUser

# Create your tests here.


class TestValidInterviewCycle(TestCase):
    """
    Test case for some arbitrary valid inputs to various Interview Cycle functions,
    including the constructor
    """

    def setUp(self) -> None:
        self.cycles = [
            InterviewCycle(
                start_date=date.today(), end_date=date.today() + timedelta(days=2),
                start_time=time(hour=5), end_time=time(hour=10),
                open_weekends=True
            ),
            InterviewCycle(
                start_date=date.today(), end_date=date.today() + timedelta(days=1),
                start_time=time(hour=5, minute=30), end_time=time(hour=5, minute=45),
                open_weekends=True
            ),
            InterviewCycle(
                start_date=date(2024, 10, 6), end_date=date(2024, 10, 6) + timedelta(days=6),
                start_time=time(hour=5, minute=30), end_time=time(hour=5, minute=45),
                open_weekends=False
            ),
            InterviewCycle(
                start_date=date(2024, 10, 6), end_date=date(2024, 10, 6) + timedelta(days=7),
                start_time=time(hour=5, minute=30), end_time=time(hour=5, minute=45),
                open_weekends=False
            ),
            InterviewCycle(
                start_date=date(2024, 10, 3), end_date=date(2024, 10, 5),
                start_time=time(hour=5, minute=30), end_time=time(hour=5, minute=45),
                open_weekends=False
            ),
        ]

    def test_valid(self):
        for cycle in self.cycles:
            cycle.clean()

    def test_num_slots(self):
        expected_num_slots = [40, 1, 5, 5, 2]
        for i in range(len(self.cycles)):
            cycle = self.cycles[i]
            self.assertEqual(cycle.num_slots, expected_num_slots[i], f"Number of slots in cycle {i} was {cycle.num_slots}, but expected {expected_num_slots[i]}.")


class TestInvalidInterviewCycle(TestCase):
    """
    Test case for ensuring that various invalid InterviewCycles fail
    validation
    """

    def setUp(self) -> None:
        self.invalid_0 = InterviewCycle(
            start_date=date.today(), end_date=date.today() + timedelta(days=-2),
            start_time=time(hour=5), end_time=time(hour=10),
            open_weekends=True
        )
        self.invalid_1 = InterviewCycle(
            start_date=date.today(), end_date=date.today() + timedelta(days=2),
            start_time=time(hour=5), end_time=time(hour=3),
            open_weekends=True
        )
        self.invalid_2 = InterviewCycle(
            start_date=date.today(), end_date=date.today() + timedelta(days=2),
            start_time=time(hour=5, minute=5), end_time=time(hour=5, minute=15),
            open_weekends=True
        )
        self.invalid_3 = InterviewCycle(
            start_date=date(2024, 10, 6), end_date=date(2024, 10, 7),
            start_time=time(hour=5, minute=5), end_time=time(hour=8),
            open_weekends=False
        )

    def test_invalid(self):
        self.assertRaises(ValidationError, self.invalid_0.clean)
        self.assertRaises(ValidationError, self.invalid_1.clean)
        self.assertRaises(ValidationError, self.invalid_2.clean)
        self.assertRaises(ValidationError, self.invalid_3.clean)

    def test_no_slots(self):
        self.assertEqual(self.invalid_3.num_slots, 0)


class TestValidInterviewAvailability(TestCase):
    def setUp(self) -> None:
        self.sampleUser = CustomUser(first_name="John", last_name="Doe", preferred_name="Johnny", email="myemail@gmail.com")
        self.cycle = InterviewCycle(
            start_date=date.today(), end_date=date.today() + timedelta(days=1),
            start_time=time(hour=5), end_time=time(hour=7),
            open_weekends=True
        )
        self.valid_0 = InterviewAvailability(slots=b'\x19', user=self.sampleUser, interview_cycle=self.cycle)

    def test_valid(self):
        self.assertEqual(self.cycle.num_slots, 8)
        self.valid_0.clean()


class TestInvalidInterviewAvailability(TestCase):
    def setUp(self) -> None:
        self.sampleUser = CustomUser(first_name="John", last_name="Doe", preferred_name="Johnny", email="myemail@gmail.com")
        self.cycle = InterviewCycle(
            start_date=date.today(), end_date=date.today() + timedelta(days=1),
            start_time=time(hour=5), end_time=time(hour=7),
            open_weekends=True
        )
        self.invalid_0 = InterviewAvailability(slots=b'\x04\x04\x04\x04', user=self.sampleUser, interview_cycle=self.cycle)

    def test_invalid(self):
        self.assertEqual(self.cycle.num_slots, 8)
        self.assertRaises(ValidationError, self.invalid_0.clean)
