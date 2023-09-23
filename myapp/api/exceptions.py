from rest_framework.exceptions import APIException

class AlreadyRegisteredException(APIException):
    status_code = 405
    default_detail = "You have already registered with this action"
    default_code = "already_registered"

class AttendanceNotPermitted(APIException):
    status_code = 403
    default_detail = "Sorry, you won't be able to attend this event"
    default_code = "attendance_disallowed"

class ActionMissing(APIException):
    status_code = 400
    default_detail = "This request hasn't specified what action you want to take on this event"
    default_code = "action_missing"

class OutsideTimeWindow(APIException):
    status_code = 403
    default_detail = "You are attempting this action outside of a valid time window." 
    default_code = "outside_time"