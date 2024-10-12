import base64
from datetime import date, time
from django.test import TestCase
from django.test.client import Client
from rest_framework.response import Response

from myapp.api.models.interviews import InterviewAvailability, InterviewCycle
from myapp.api.models.users import CustomUser, InductionClass


class TestInterviewCycleViews(TestCase):
    def setUp(self) -> None:
        """
        Create an induction class, one superuser, one normal user, and
        one availability per existing user. Also create 2 logged-in clients,
        one for each user.
        """
        self.induction_class = InductionClass.objects.create_induction_class(
            name="Beta Tau",
            start_date=date(2024, 9, 26),
            end_date=date(2024, 12, 14),
            academic_year=2024,
        )
        self.interview_cycle = InterviewCycle.objects.create(
            start_date=date(2024, 10, 10),
            end_date=date(2024, 10, 11),
            open_weekends=False,
            start_time=time(hour=10),
            end_time=time(hour=20),
            induction_class=self.induction_class
        )

        self.superuser1 = CustomUser.objects.create_superuser(
            first_name="Roger",
            last_name="Lin",
            password="verysecurepass",
            preferred_name="Raggy",
            pronouns="he/him",
            email="rlin@ucsd.edu",
            induction_class=self.induction_class
        )
        self.superuser1_client = Client()
        self.superuser1_client.login(username="rlin@ucsd.edu", password="verysecurepass")
        self.superuser1_availability = InterviewAvailability.objects.create(
            slots=b"\x0f\xf0\x0f\xf0\x0f",
            user=self.superuser1,
            interview_cycle=self.interview_cycle
        )

        self.user1 = CustomUser.objects.create_user(
            first_name="Ryan",
            last_name="Lee",
            password="verysecurepass2",
            preferred_name="Ryan",
            pronouns="he/him",
            email="rsl@ucsd.edu",
            induction_class=self.induction_class
        )
        self.user1_client = Client()
        self.user1_client.login(username="rsl@ucsd.edu", password="verysecurepass2")
        self.user1_availability = InterviewAvailability.objects.create(
            slots=b"\xaa\xbb\xaa\xbb\xaa",
            user=self.user1,
            interview_cycle=self.interview_cycle
        )

        self.anon_client = Client()

    def test_admin_get_interview_cycle_list(self):
        response = self.superuser1_client.get("/api/interviewcycles", follow=True)
        response_to_dicts = [dict(ord_dict) for ord_dict in response.data]
        expected = [
            {
                "start_date": f"{self.interview_cycle.start_date.year}-{self.interview_cycle.start_date.month}-{self.interview_cycle.start_date.day}",
                "end_date": f"{self.interview_cycle.end_date.year}-{self.interview_cycle.end_date.month}-{self.interview_cycle.end_date.day}",
                "open_weekends": self.interview_cycle.open_weekends,
                "start_time": f"{self.interview_cycle.start_time.hour:02d}:{self.interview_cycle.start_time.minute:02d}:{self.interview_cycle.start_time.second:02d}",
                "end_time": f"{self.interview_cycle.end_time.hour:02d}:{self.interview_cycle.end_time.minute:02d}:{self.interview_cycle.end_time.second:02d}",
                "induction_class": f"{self.interview_cycle.induction_class.name}",
                "availabilities": [availability.pk for availability in self.interview_cycle.availabilities.all()]
            }
        ]
        self.assertEqual(expected, response_to_dicts)

    def test_member_get_interview_cycle_list(self):
        response = self.user1_client.get("/api/interviewcycles", follow=True)
        response_to_dicts = [dict(ord_dict) for ord_dict in response.data]
        expected = [
            {
                "start_date": f"{self.interview_cycle.start_date.year}-{self.interview_cycle.start_date.month}-{self.interview_cycle.start_date.day}",
                "end_date": f"{self.interview_cycle.end_date.year}-{self.interview_cycle.end_date.month}-{self.interview_cycle.end_date.day}",
                "open_weekends": self.interview_cycle.open_weekends,
                "start_time": f"{self.interview_cycle.start_time.hour:02d}:{self.interview_cycle.start_time.minute:02d}:{self.interview_cycle.start_time.second:02d}",
                "end_time": f"{self.interview_cycle.end_time.hour:02d}:{self.interview_cycle.end_time.minute:02d}:{self.interview_cycle.end_time.second:02d}",
                "induction_class": f"{self.interview_cycle.induction_class.name}"
            }
        ]
        self.assertEqual(expected, response_to_dicts)

    def test_anon_get_interview_cycle_list(self):
        response = self.anon_client.get("/api/interviewcycles", follow=True)
        self.assertEqual(response.status_code, 401)

    def test_admin_get_interview_cycle(self):
        response = self.superuser1_client.get(f"/api/interviewcycles/{self.interview_cycle.pk}", follow=True)
        response_to_dict = dict(response.data)
        expected = {
            "start_date": f"{self.interview_cycle.start_date.year}-{self.interview_cycle.start_date.month}-{self.interview_cycle.start_date.day}",
            "end_date": f"{self.interview_cycle.end_date.year}-{self.interview_cycle.end_date.month}-{self.interview_cycle.end_date.day}",
            "open_weekends": self.interview_cycle.open_weekends,
            "start_time": f"{self.interview_cycle.start_time.hour:02d}:{self.interview_cycle.start_time.minute:02d}:{self.interview_cycle.start_time.second:02d}",
            "end_time": f"{self.interview_cycle.end_time.hour:02d}:{self.interview_cycle.end_time.minute:02d}:{self.interview_cycle.end_time.second:02d}",
            "induction_class": f"{self.interview_cycle.induction_class.name}",
            "availabilities": [availability.pk for availability in self.interview_cycle.availabilities.all()]
        }
        self.assertEqual(expected, response_to_dict)

    def test_member_get_interview_cycle(self):
        response = self.user1_client.get(f"/api/interviewcycles/{self.interview_cycle.pk}", follow=True)
        response_to_dict = dict(response.data)
        expected = {
            "start_date": f"{self.interview_cycle.start_date.year}-{self.interview_cycle.start_date.month}-{self.interview_cycle.start_date.day}",
            "end_date": f"{self.interview_cycle.end_date.year}-{self.interview_cycle.end_date.month}-{self.interview_cycle.end_date.day}",
            "open_weekends": self.interview_cycle.open_weekends,
            "start_time": f"{self.interview_cycle.start_time.hour:02d}:{self.interview_cycle.start_time.minute:02d}:{self.interview_cycle.start_time.second:02d}",
            "end_time": f"{self.interview_cycle.end_time.hour:02d}:{self.interview_cycle.end_time.minute:02d}:{self.interview_cycle.end_time.second:02d}",
            "induction_class": f"{self.interview_cycle.induction_class.name}",
        }
        self.assertEqual(expected, response_to_dict)

    def test_anon_get_interview_cycle(self):
        response = self.anon_client.get(f"/api/interviewcycles/{self.interview_cycle.pk}", follow=True)
        self.assertEqual(response.status_code, 401)

    def test_admin_get_interview_avail_list(self):
        response = self.superuser1_client.get(f"/api/interviewavailabilities")
        response_to_dict = [dict(dict_in_response) for dict_in_response in response.data]
        expected = [
            {
                "slots": base64.b64encode(self.superuser1_availability.slots).decode("utf-8"),
                "user": self.superuser1_availability.user.pk,
                "interview_cycle": self.superuser1_availability.interview_cycle.pk
            },
            {
                "slots": base64.b64encode(self.user1_availability.slots).decode("utf-8"),
                "user": self.user1_availability.user.pk,
                "interview_cycle": self.user1_availability.interview_cycle.pk
            },
        ]

        # TODO: This test is currently quite brittle. Change to a set equality check instead of array equality check
        self.assertEqual(expected, response_to_dict)

    def test_admin_get_interview_avail_list_filtered(self):
        response = self.superuser1_client.get(f"/api/interviewavailabilities?interview_cycle={self.interview_cycle.pk}")
        response_to_dict = [dict(dict_in_response) for dict_in_response in response.data]
        expected = [
            {
                "slots": base64.b64encode(self.superuser1_availability.slots).decode("utf-8"),
                "user": self.superuser1_availability.user.pk,
                "interview_cycle": self.superuser1_availability.interview_cycle.pk
            },
            {
                "slots": base64.b64encode(self.user1_availability.slots).decode("utf-8"),
                "user": self.user1_availability.user.pk,
                "interview_cycle": self.user1_availability.interview_cycle.pk
            },
        ]

        # TODO: This test is currently quite brittle. Change to a set equality check instead of array equality check
        self.assertEqual(expected, response_to_dict)

    def test_admin_get_interview_avail_list_filtered_nonexist(self):
        response = self.superuser1_client.get("/api/interviewavailabilities?interview_cycle=50")
        expected = []
        self.assertEqual(response.status_code, 400)

    def test_member_get_interview_avail_list(self):
        response = self.user1_client.get(f"/api/interviewavailabilities")
        response_to_dict = [dict(dict_in_response) for dict_in_response in response.data]
        expected = [
            {
                "slots": base64.b64encode(self.user1_availability.slots).decode("utf-8"),
                "user": self.user1_availability.user.pk,
                "interview_cycle": self.user1_availability.interview_cycle.pk
            },
        ]

        # TODO: This test is currently quite brittle. Change to a set equality check instead of array equality check
        self.assertEqual(expected, response_to_dict)

    def test_anon_get_interview_avail_list(self):
        response = self.anon_client.get("/api/interviewavailabilities")
        self.assertEqual(response.status_code, 401)

    def test_admin_get_interview_avail(self):
        response = self.user1_client.get(f"/api/interviewavailabilities/{self.user1_availability.pk}")
        response_to_dict = dict(response.data)
        expected = {
            "slots": base64.b64encode(self.user1_availability.slots).decode("utf-8"),
            "user": self.user1_availability.user.pk,
            "interview_cycle": self.user1_availability.interview_cycle.pk
        }
        self.assertEqual(response_to_dict, expected)

    def test_member_get_interview_avail(self):
        response = self.user1_client.get(f"/api/interviewavailabilities/{self.user1_availability.pk}")
        response_to_dict = dict(response.data)
        expected = {
            "slots": base64.b64encode(self.user1_availability.slots).decode("utf-8"),
            "user": self.user1_availability.user.pk,
            "interview_cycle": self.user1_availability.interview_cycle.pk
        }
        self.assertEqual(response_to_dict, expected)

    def test_anon_get_interview_avail(self):
        response = self.anon_client.get(f"/api/interviewavailabilities/{self.user1_availability.pk}")
        self.assertEqual(response.status_code, 401)

    def test_admin_put_interview_cycle(self):
        pass

    def test_member_put_interview_cycle(self):
        pass

    def test_anon_put_interview_cycle(self):
        pass

    def test_admin_patch_interview_cycle(self):
        pass

    def test_member_patch_interview_cycle(self):
        pass

    def test_anon_patch_interview_cycle(self):
        pass

    def test_admin_del_interview_cycle(self):
        pass

    def test_member_del_interview_cycle(self):
        pass

    def test_anon_del_interview_cycle(self):
        pass
