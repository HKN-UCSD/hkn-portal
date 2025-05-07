from zoneinfo import ZoneInfo
from datetime import datetime

# made this to test out the zoneinfo stuff, no need for the zoneinfo package (i can't install it anyways LOL)
dt = datetime(2025, 5, 7, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
print(dt)