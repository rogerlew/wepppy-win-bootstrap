
def isint(x):
    # noinspection PyBroadException
    try:
        return float(int(x)) == float(x)
    except Exception:
        return False
