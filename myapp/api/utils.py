from django.utils import timezone

def inwindow(event, action):
    leewayed_start = event.start_time - action.start_leeway
    leewayed_end = event.end_time + action.end_leeway
    before = timezone.now() < leewayed_start
    middle = timezone.now() >= leewayed_start and timezone.now() < leewayed_end
    after = timezone.now() >= leewayed_end

    allwindows = {
        0b000: False,
        0b001: after,
        0b010: middle,
        0b011: after or middle,
        0b100: before,
        0b101: before or after,
        0b110: before or middle,
        0b111: True
    }

    return allwindows[action.window]