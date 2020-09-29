
from datetime import datetime, timedelta, date

def determine_wateryear(y, j=None, mo=None):
    if j is not None:
        mo = int((datetime(int(y), 1, 1) + timedelta(int(j))).month)

    if mo > 9:
        return y + 1

    return y
def isint(x):
    # noinspection PyBroadException
    try:
        return float(int(x)) == float(x)
    except Exception:
        return False
