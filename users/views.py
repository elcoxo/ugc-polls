from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.shortcuts import redirect, render
from rest_framework.generics import get_object_or_404

from polls.models import Poll, PollSession


def register(request):
    """Простая регистрация через форму"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def poll_statistics(request, slug):
    """Статистика опроса для автора"""
    poll = get_object_or_404(Poll, slug=slug, user=request.user)

    sessions = PollSession.objects.filter(poll=poll)
    completed = sessions.filter(finished_at__isnull=False)

    # среднее время
    avg_time = None
    if completed.exists():
        durations = [s.duration.total_seconds() for s in completed if s.duration]
        avg_time = int(sum(durations) / len(durations)) if durations else None

    # статистика ответов по каждому вопросу
    data = []
    for question in poll.questions.prefetch_related('options'):
        options = question.options.annotate(response_count=Count('userresponse'))

        options_data = []
        total = 0
        for o in options:
            options_data.append(
                {
                    'text': o.text,
                    'count': o.response_count,
                }
            )
            total += o.response_count

        for option in options_data:
            option['percentage'] = round(option['count'] / total * 100) if total else 0

        data.append(
            {
                'text': question.text,
                'total': total,
                'options': options_data,
            }
        )

    return render(request, 'users/poll_statistics.html', {
        'poll': poll,
        'total_sessions': sessions.count(),
        'completed_sessions': completed.count(),
        'avg_completion_seconds': avg_time,
        'questions': data,
    })
