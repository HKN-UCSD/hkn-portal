from myapp.api.exceptions import ForbiddenException
from myapp.api.permissions import is_admin
from myapp.api.models.users import CustomUser
from myapp.api.models.events import Event, EventActionRecord
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from django.utils import timezone

# Don't touch!!!
self_action_registry = {}
other_action_registry = {}
eventless_action_registry = {}
action_registry = {}


def event_action(name, self_only=False, eventless=False):
    """
    Decorator indicating an event action. Functions with this decorator should
    automatically be viewable in the api, by calling /api/eventactions/.
    When a POST request is made to the event_actions database, the server
    executes the function with the appropriate name. If necessary, such
    functions can raise an exception to prevent the action from taking place,
    such as if the user lacks permission.

    Event actions must have two parameters. The first will take request data
    that was initially obtained by the EventActionRecord viewset. The second
    will take the data about the event action, sent in via the request body.

    Event action records consist of a subject, a verb, and an object, much like
    sentences. In the database, the subject is stored as `user`, the verb as
    `action`, and the object as `acted_on`. So, an event action record can
    record "user 1 checked off user2" or "user 3 checked off user 3".

    By default, an action will be considered part of `other_actions`,
    performable by
    some user on another or themselves. The self_only parameter indicates that
    users can only perform this action on themselves.

    `eventless` is not yet implemeneted, but the idea is that actions with
    `eventless` turned on are actions some
    users can perform, irrespective of events. For example, under special
    circumstances, an officer might grant some points to a member, without
    the member having attended an event.
    """

    def register(func):
        curfunc = func
        if eventless:

            def wrapper(request, data):
                if data["event"] != None and data["event"] != "":
                    raise ForbiddenException
                func(request, data)

            curfunc = wrapper

        if self_only is True:

            def wrapper(request, data):
                acted_on = CustomUser.objects.get(user_id=data["acted_on"])
                if request.user.pk != acted_on.pk:
                    raise ForbiddenException
                func(request, data)

            curfunc = wrapper

        action_registry[name] = curfunc
        if eventless:
            eventless_action_registry[name] = curfunc

        if self_only:
            self_action_registry[name] = curfunc
        else:
            other_action_registry[name] = curfunc

        return curfunc

    return register


event_action.self_actions = self_action_registry
event_action.other_actions = other_action_registry
event_action.eventless_actions = eventless_action_registry
event_action.all = action_registry
# Okay now you can start coding below this line
# decorate a function with @event_action, and it'll be considered an event action.
# Make sure it takes a request object, and to give the action a name (this is the
# name used for buttons).
# If the action should fail, you should raise an error; this will prevent
# any the action from being recorded.
# There should be no return value
# Permissions to perform an action should be programatically checked inside the action's function body
# (sorry this is a kinda rudimentary solution); permissions are automatically created.
# Names should be distinct even if all characters were lower-case


@event_action(name="RSVP", self_only=True)
def rsvp(request, data):
    # Time restriction
    event_to_check_time_of = Event.objects.get(pk=data["event"])
    if event_to_check_time_of.is_time_restricted and timezone.now() > event_to_check_time_of.start_time:
        raise ForbiddenException("You can only RSVP before an event")
    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        raise ForbiddenException("Could not find the user attempting the rsvp")

    if (
        acted_on.actions_received.all()
        .filter(event__pk=data["event"], action="RSVP")
        .exists()
    ):
        raise ForbiddenException("Already RSVP'd")


@event_action(name="Sign In", self_only=True)
def signup(request, data):
    # Time restriction
    event_to_check_time_of = Event.objects.get(pk=data["event"])
    if event_to_check_time_of.is_time_restricted:
        if timezone.now() < event_to_check_time_of.start_time - timedelta(
            minutes=15
        ) or timezone.now() > event_to_check_time_of.end_time + timedelta(minutes=15):
            raise ForbiddenException(
                "You can only sign in during an event, or 15 minutes before one."
            )

    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        raise ForbiddenException("Could not find the user signing in")

    if (
        acted_on.actions_received.all()
        .filter(event__pk=data["event"], action="Sign In")
        .exists()
    ):
        raise ForbiddenException("Already signed in")

@event_action(name="Check Off")
def checkoff(request, data):
    # Time restriction
    event_to_check_time_of = Event.objects.get(pk=data["event"])
    if event_to_check_time_of.is_time_restricted and timezone.now() < event_to_check_time_of.start_time:
        raise ForbiddenException("Check-off can only be done during or after an event")

    # if the acted_on user is not in the list of people who have signed up, error.
    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        raise ForbiddenException("Could not find the user being checked off")

    if (
        not acted_on.actions_received.all()
        .filter(event__pk=data["event"], action="Sign In")
        .exists()
    ):
        raise ForbiddenException("Not yet signed in")

    if (
        acted_on.actions_received.all()
        .filter(event__pk=data["event"], action="Check Off")
        .exists()
    ):
        raise ForbiddenException("This user has already been checked off")

    # if the user is does not have permission to check off, error
    if not is_admin(request.user):
        raise ForbiddenException("No permission to check off")
    