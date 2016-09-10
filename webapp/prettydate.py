from datetime import datetime


def _df(seconds, denominator=1, text='', past=True):
    if past:
        return '{} {} ago'.format(
            int((seconds + denominator / 2) / denominator), text)
    else:
        return 'in {} {}'.format(
            int((seconds + denominator / 2) / denominator), text)


def date(time=False, now=datetime.utcnow()):
    if type(time) is int:
        time = datetime.fromtimestamp(time)
    elif not time:
        time = now

    if time > now:
        past, diff = False, time - now
    else:
        past, diff = True,  now - time

    seconds = diff.seconds
    days = diff.days

    if days == 0:
        if seconds < 10:
            return 'now'
        elif seconds < 60:
            return _df(seconds, 1, ' seconds', past)
        elif seconds < 120:
            return past and 'a minute ago' or 'in a minute'
        elif seconds < 3600:
            return _df(seconds, 60, ' minutes', past)
        elif seconds < 7200:
            return past and 'an hour ago' or'in an hour'
        else:
            return _df(seconds, 3600, ' hours', past)
    else:
        if days == 0:
            return 'today'
        elif days == 1:
            return past and 'yesterday' or'tomorrow'
        elif days == 2:
            return past and 'day before' or 'day after'
        elif days < 7:
            return _df(days, 1, ' days', past)
        elif days < 14:
            return past and 'last week' or 'next week'
        elif days < 31:
            return _df(days, 7, ' weeks', past)
        elif days < 61:
            return past and 'last month' or 'next month'
        elif days < 365:
            return _df(days, 30, ' months', past)
        elif days < 730:
            return past and 'last year' or 'next year'
        else:
            return _df(days, 365, ' years', past)
