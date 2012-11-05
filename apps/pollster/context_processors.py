from apps import pollster

from apps.survey.views import _get_health_history

def last_survey(request):
    try:
        survey = pollster.models.Survey.get_by_shortname('weekly')
    except:
        return {}

    history = list(_get_health_history(request, survey))
    if not history:
        return {}

    surveyuser_qs = request.user.surveyuser_set.filter(deleted=False)
    return {
        'last_survey': history[-1],
        'surveyuser_count': surveyuser_qs.count(),
        'surveyuser_gid': surveyuser_qs.get().global_id if surveyuser_qs.count() == 1 else None,
    }
