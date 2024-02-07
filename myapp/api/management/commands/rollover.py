from django.core.management.base import BaseCommand
from myapp.api.models.events import EventActionRecord, Event
from myapp.api.models.users import CustomUser, Inductee, InductionClass
from django.utils import timezone, dateformat
import json

class Command(BaseCommand):
    help = "Move all rollover points to general points"

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*")

    def handle(self, *args, **kwargs):
        with open(args[0], "r") as f:
             data = json.load(f)
        
        MAX_ROLLOVER_POINTS = 3
        ROLLOVER_EVENT = InductionClass.objects.filter(name = "Beta Omicron").first().rollover_event
        ROLLOVER_EVENT_ID = Event.objects.filter(name = ROLLOVER_EVENT).first().pk
        result = []

        users = CustomUser.objects.filter(induction_class__name = "Beta Omicron")
        inductees = []
        for user in users:
            inductees.append(str(user.user_id))

        # Get all non-first time inductees
        for id in data:
            user = CustomUser.objects.filter(user_id = id).first()
            try:
                (data[id]["first time inductee"])
                print(user)
                inductees.remove(id)
            except:
                continue

        validTimeStart = timezone.make_aware(timezone.datetime(2023, 9, 30))
        validTimeEnd = timezone.make_aware(timezone.datetime(2024, 1, 8))

        for inductee in inductees:
            user = Inductee.objects.filter(user = inductee).first()
            cleared = []
            points = 0
            userActionRecords = EventActionRecord.objects.filter(action = "Check Off", acted_on__user_id = inductee)
            for record in userActionRecords:
                # All points earned in previous cycle
                if (record.action_time > validTimeStart) and (record.action_time < validTimeEnd):
                    cleared.append(str(record.pk) + ": " + record.event.name + ", " + str(record.points))
                    points += record.points
                    # Set record points to 0 to clear points
                    # record.points = 0
                    # record.save()
            #print(cleared)
            points = min(points, MAX_ROLLOVER_POINTS)
            resultRecord = {user: {"cleared":cleared, "rollover": points}}

            if (points != 0):
                customUser = CustomUser.objects.filter(user_id = inductee).first()
                print(customUser)
                sign_in = EventActionRecord.objects.create(
                    action = "Sign In",
                    acted_on = customUser,
                    event_id = ROLLOVER_EVENT_ID,
                    user = customUser,
                )
                sign_in.save()

                check_off = EventActionRecord.objects.create(
                    action = "Check Off",
                    acted_on = customUser,
                    event_id = ROLLOVER_EVENT_ID,
                    user = customUser,
                    points = points,
                )
                check_off.save()

                resultRecord[user]["rollover action"] = check_off.pk
                result.append(resultRecord)

        for record in result:
            for item in record:
                print(item)
                print(record[item])