from apps.programmes.models import Episode
from apps.schedules.models import Schedule


def available_dates(programme, after):
    schedules = Schedule.objects.filter(programme=programme, type='L')

    while True:
        candidates = (
            filter(lambda s: s is not None,
                   map(lambda s: s.date_after(after, inc=False),
                       schedules)))
        try:
            # XXX there may be two parallel slots, use reduce
            next = min(candidates)
        except ValueError:
            break;

        yield next
        after = next


# XXX transaction?
def rearrange_episodes(programme, after):
    episodes = Episode.objects.unfinished(programme, after)
    dates = available_dates(programme, after)

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
