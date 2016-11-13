import datetime


def next_dates(programme, after):
    """
    Returns: A generator with the next dates of a given programme
    """
    from radioco.apps.schedules.models import Schedule
    schedules = Schedule.objects.filter(programme=programme, type='L')

    while True:
        candidates = map(lambda s: s.date_after(after), schedules)
        try:
            next_date = min(candidates)
        except ValueError:
            break

        yield next_date
        after = next_date + datetime.timedelta(seconds=1)
        # schedules = filter(lambda t: t[1] is not None, zip(schedules, candidates))
        schedules = [_tuple[0] for _tuple in zip(schedules, candidates) if _tuple[1] is not None]


# XXX transaction?
def rearrange_episodes(programme, after):
    """
    Update the issue_date of next episodes from a given date
    """
    from radioco.apps.programmes.models import Episode
    episodes = Episode.objects.unfinished(programme, after)
    dates = next_dates(programme, after)

    # Further dates and episodes available -> re-order
    while True:
        try:
            date = dates.next()
            episode = episodes.next()
        except StopIteration:
            break

        episode.issue_date = date
        episode.save()

    # No further dates available -> unschedule
    while True:
        try:
            episode = episodes.next()
        except StopIteration:
            break

        episode.issue_date = None
        episode.save()
