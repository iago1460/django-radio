import datetime


def next_dates(calendar, programme, after):
    """
    Returns: A generator with the next dates of a given programme
    """
    if not calendar or not calendar.id:
        return

    from radioco.apps.schedules.models import Schedule
    # Only taking into account schedules which belong to the active calendar
    schedules = Schedule.objects.filter(programme=programme, type='L', calendar=calendar)

    while True:
        candidates = map(lambda s: s.date_after(after), schedules)
        try:
            next_date = min(filter(lambda _dt: _dt is not None, candidates))
        except ValueError:
            break

        yield next_date
        after = next_date + datetime.timedelta(seconds=1)
        # schedules = filter(lambda t: t[1] is not None, zip(schedules, candidates))
        schedules = [_tuple[0] for _tuple in zip(schedules, candidates) if _tuple[1] is not None]

