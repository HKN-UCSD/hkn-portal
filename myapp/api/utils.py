from django.utils import timezone
from io import StringIO
from django.core.management import call_command

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


def sync_house_points_from_events():
    """
    Runs the sync_house_sheet management command and returns the result.
    By default, does NOT clear existing data. To preserve user memberships and assignments.
    """
    try:
        out = StringIO()
        # Note: NOT using --clear flag to preserve existing memberships
        call_command('sync_house_sheet', stdout=out)
        output = out.getvalue()
        
        return {
            'success': True,
            'message': 'Sync successful! House points have been updated from the source sheet.'
        }
    except Exception as e:
        error_msg = str(e)
        return {
            'success': False,
            'message': f'Sync failed: {error_msg}'
        }