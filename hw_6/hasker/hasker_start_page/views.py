import datetime
import math

from django.shortcuts import render
from hasker_posts.models import Questions, Answers, Tags


def time_normalyser(secs):
    days = math.floor((secs / 86400))
    hours = math.floor((secs - days * 86400) / 3600)
    mins = math.floor((secs - (days * 86400 + hours * 3600)) / 60)
    seconds = secs - (days * 86400 + hours * 3600 + mins * 60)

    formatted_date = 'Asked {0}{1}{2}{3} ago'.format('Days ' + str(days) + ', ' if days > 0 else '',
                                                     'hours ' + str(hours) + ', ' if hours > 0 else '',
                                                     'minutes ' + str(mins) + ', ' if mins > 0 else '',
                                                     'seconds ' + str(seconds) if seconds > 0 else '')

    return formatted_date


def time_delta_generator(datetimeobj):
    tz_info = datetimeobj.tzinfo
    diff = round((datetime.datetime.now(tz_info) - datetimeobj).total_seconds())
    formatted_time = time_normalyser(diff)
    return formatted_time


def tags_decoder(tags):
    result = []
    if tags is not None:
        for tag in tags.split(','):
            t = list(Tags.objects.filter(id=tag).values())
            result.append(t[0]['tag'])
    return result


def get_start_page(request):
    result = []
    new_questions = list(Questions.objects.select_related().all().values()[:5])

    for question in new_questions:
        new_q = question

        answers = Answers.objects.filter(question=question['id']).count()
        new_q.update({'answers': answers})

        tags = tags_decoder(question['tags'])
        new_q.update({'tags': tags})

        tfc = {'time_from_creation': time_delta_generator(question['created'])}
        new_q.update(tfc)

        result.append(new_q)

    data = {'new_questions': result}
    return render(request, 'index.html', context=data)
