

class Julian(object):
    def __init__(self, *args, **kwargs):

        # noinspection PyUnusedLocal
        __slots__ = ["julian", "month", "day"]

        if len(kwargs) > 0:
            assert "julian" in kwargs
            julian = kwargs['julian']
            assert julian > 0
            assert julian <= 365

            assert "month" in kwargs
            assert "day" in kwargs
            month = kwargs['month']
            day = kwargs['day']

            _m, _d = julian_to_md(julian)
            assert _m == month
            assert _d == day

            super(Julian, self).__setattr__("julian", julian)
            super(Julian, self).__setattr__("month", month)
            super(Julian, self).__setattr__("day", day)

        if len(args) == 1:
            julian = int(args[0])
            assert julian >= 0
            assert julian <= 365

            super(Julian, self).__setattr__("julian", julian)

            month, day = julian_to_md(julian)
            super(Julian, self).__setattr__("month", month)
            super(Julian, self).__setattr__("day", day)

        elif len(args) == 2:
            month = int(args[0])
            day = int(args[1])
            assert month > 0
            assert month <= 12

            assert day > 0
            assert day <= _days[month-1]

            super(Julian, self).__setattr__("month", month)
            super(Julian, self).__setattr__("day", day)

            julian = md_to_julian(month, day)
            super(Julian, self).__setattr__("julian", julian)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return str(self.julian)

    def __repr__(self):
        # noinspection PyUnresolvedReferences
        return 'Julian(julian=%i, month=%i, day=%i)'\
               % (self.julian, self.month, self.day)
               
def parse_julian(x):
    foo = int(x)
    if foo == 0:
        return foo
    else:
        return Julian(foo)


_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_cummdays = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]


def julian_to_md(julian):
    for i, (d, cd) in enumerate(zip(_days, _cummdays)):
        if julian <= cd:
            return i+1, d - (cd - julian)


def md_to_julian(month, day):
    return _cummdays[month-1] + day - _days[month-1]
