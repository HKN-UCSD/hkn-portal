from myapp.api.exceptions import ForbiddenException
from myapp.api.permissions import is_admin
from myapp.api.models.users import CustomUser
from myapp.api.models.events import Event, EventActionRecord
from django.core.exceptions import ObjectDoesNotExist

# Don't touch!!!
self_action_registry = {}
other_action_registry = {}
eventless_action_registry = {}
action_registry = {}


def event_action(name, self_only=False, eventless=False):
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
    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        print("Could not find the user attempting the rsvp")
        raise ForbiddenException("Could not find the user attempting the rsvp")

    if (
        acted_on.actions_taken.all()
        .filter(event__pk=data["event"], action="RSVP")
        .exists()
    ):
        print("Already RSVP'd")
        raise ForbiddenException("Already RSVP'd")
        
    print("I just rsvp'd")


@event_action(name="Sign In", self_only=True)
def signup(request, data):
    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        print("Could not find the user signing in")
        raise ForbiddenException("Could not find the user signing in")

    if (
        acted_on.actions_taken.all()
        .filter(event__pk=data["event"], action="Sign In")
        .exists()
    ):
        print("Already signed in")
        raise ForbiddenException("Already signed in")

    print("I just signed up. The action is: " + str(data["action"]))


@event_action(name="Check Off")
def checkoff(request, data):
    # if the acted_on user is not in the list of people who have signed up, error.
    try:
        acted_on = CustomUser.objects.get(user_id=data["acted_on"])
    except ObjectDoesNotExist:
        print("Could not find the user being checked off")
        raise ForbiddenException("Could not find the user being checked off")

    if (
        not acted_on.actions_taken.all()
        .filter(event__pk=data["event"], action="Sign In")
        .exists()
    ):
        print("Not yet signed in")
        raise ForbiddenException("Not yet signed in")
    
    if (
        acted_on.actions_taken.all()
        .filter(event__pk=data["event"], action="Check Off")
        .exists()
    ):
        print("Already Checked off")
        raise ForbiddenException("This user has already been checked off")

    # if the user is does not have permission to check off, error
    if not is_admin(request.user):
        print("No permission to check off")
        raise ForbiddenException("No permission to check off")

    # if the above two checks are passed, we are free to check off.
    print(f"Checking off with {data}")