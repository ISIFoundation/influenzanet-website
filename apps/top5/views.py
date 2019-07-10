from datetime import datetime
from random import shuffle

from django.shortcuts import  render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
#from django.template import RequestContext, loader

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login

from .models import Service, Ranking, Part, get_service, formating_part

from apps.reminder.views import json_dumps

#Redirection according to the user progress
@login_required
def index(request):
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)
    if Ranking.objects.filter(user = user).count() == 0 :
        return render(request, 'presentation.html')
    ranking_user = Ranking.objects.filter(user = user)

    done = False #checking : did user already answer the survey?
    for r in ranking_user :
        if r.rank != 0 and r.rank is not None :
            done = True
            break
    if done :
        return HttpResponseRedirect('/survey/run/top5-patients/')

    nb_ranked = ranking_user.filter(pertinency = 1).count()
    if(nb_ranked == 5):
        return redirect(ranking)

    return redirect(selection_service)


# show the 15 services ordered randomly
def selection_service(request):
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)
    services = list(Service.objects.all())
    shuffle(services)
    ranking_user = Ranking.objects.filter(user = user)
    nb_ranked = ranking_user.filter(pertinency = 1).count()
    context = {
        'services' : services,
        'user' : user,
        'ranking' : ranking_user,
        'ranking_size' : nb_ranked,
    }

    return render(request, 'questionnaire.html', context)


# Used for saving date when user close the tab with
def closing_tab(request):
    now = datetime.now()
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)
    service_id = request.POST.get('service', None)
    try:
        User_ranking = Ranking.objects.filter(user = user)
        ranking_service = User_ranking.get(service_id = service_id)
        ranking_service.closing_tab_date = now
        ranking_service.save()
        data = {
                'close': '1',
                }
        data_json = json_dumps(data)
        status = 200
    except Exception, e:
        status = 500
        data_json = "An error occurred during closing tab :\n" + str(e)

    return HttpResponse(data_json, content_type="application/json", status=status)

# creation into ranking table of an empty rank for an user and a specific service when opening the tab
@csrf_protect
def creation_rank(request):
    now = datetime.now()
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)

    service_id = request.POST.get('service', None)
    try:
        ranking_user = Ranking.objects.filter(user = user)
        if(ranking_user.filter(service_id = service_id).count() == 0):
            service = Service.objects.get(id = service_id)
            ranking_service = Ranking.objects.create(user = user, service_id = service, creation_date = now, pertinency = 0)
            data = {
                'action': "Creation",
            }
            ranking_service.save()
        else:
            data = {
                'action': "None",
            }
        res = json_dumps(data)
    except Exception, e:
        res = "An error occurred during creation :\n" + str(e)
    return HttpResponse(res, content_type="application/json")


# change pertinency of a rank for an user and a specific service when clicking on the main button
@csrf_protect
def chgmt_statut_service(request):
    now = datetime.now()
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)
    service_id = request.POST.get('service', None)
    pertinency = request.POST.get('pertinency', None)
    User_ranking = Ranking.objects.filter(user = user)
    try :
        data = {
            'exists': 1,
        }
        if(User_ranking.filter(service_id = service_id).count() != 0):
            ranking_service = User_ranking.get(service_id = service_id)
            ranking_service.pertinency = pertinency
            if pertinency == '0' :
                #reset rank values because the service is unselected
                ranking_service.temporary_rank = 0
                ranking_service.rank = 0   # laisser pour les tests, mais normalement pas besoin car rank n'est enregistre que a la fin?
                ranking_service.service_selection_date = None
                ranking_service.top5_selection_date = None
                ranking_service.modif_date = now
            else :
                if ranking_service.service_selection_date :
                    ranking_service.modif_date = now
                    data.update({'action' : "modification"})
                else :
                    ranking_service.service_selection_date = now
                    data.update({'action' : "selection"})
        else:
            service = Service.objects.get(id = service_id)
            ranking_service = Ranking.objects.create(user = user, service_id = service, creation_date = now, pertinency = 1)
            data.update({'action' : "creation"})
        ranking_service.save()
        nbRated = Ranking.objects.filter(user = user, pertinency = 1).count()
        data.update({'nbRated' : nbRated})
        data_json = json_dumps(data)
        status = 200
    except Exception, e:
        status = 500
        data_json = "An error occurred during the changement:\n" + str(e)
    return HttpResponse(data_json, content_type="application/json", status=status)


#Get the list o the 5 selected services (pertinency = 1), try to order it and return into the ranking page
@login_required
def ranking(request): #,action
    user = request.user
    if user == 'AnonymousUser':
        redirect(auth_login)
    now = datetime.now()

    ranking_user = Ranking.objects.filter(user = user)
    ranking = ranking_user.filter(pertinency = 1).order_by('temporary_rank')
    if request.POST :
        for ranked_service in ranking :
            ranked_service.top5_selection_date = now
            ranked_service.save()
    context = {
        'user' : user,
        'ranking' : ranking,
    }
    return render(request, 'ranking.html', context)


    # Save the rank into temporary_rank or rank
@csrf_protect
def saving_rank(request):
    now = datetime.now()
    if request.POST :
        post = request.POST
        user = request.user
        if user == 'AnonymousUser':
            redirect(auth_login)
        ranking = Ranking.objects.filter(user = user).filter(pertinency = 1)

    if post.get("save") == 'final' :
        for rank in ranking :
            rank.temporary_rank = post.get("hidden-rank-"+str(rank.id))
            rank.rank = post.get("hidden-rank-"+str(rank.id))
            rank.validation_date = now
        return HttpResponseRedirect('/survey/run/top5-patients/')
    else:
        for rank in ranking :
            rank.temporary_rank = post.get("hidden-rank-"+str(rank.id))
            rank.modif_date = datetime.now()
            rank.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return render(request, '/survey/top5-patients/')



    # Formating the full text of a service from the diferrent part texts
@staff_member_required
def create_service_html(request, service_id):
    service = get_service(service_id)
    parts_service = Part.objects.filter(service = service).order_by('part_type')
    temp_text = ""
    for part in parts_service :
        part_text = formating_part(part)
        temp_text = temp_text + part_text

    service.text_html = temp_text
    service.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# TODO in construction : For a specific service, Get all the ranks validated by users and calculate top5 score
@staff_member_required
def calcul_score(request, service_id):
    service = get_service(service_id)
    all_ranked = Ranking.objects.filter(service = service).filter(pertinency = 1)

    temp_text = ""
    for part in all_ranked :
        part_text = formating_part(part)
        temp_text = temp_text + part_text

    service.text_html = temp_text
    service.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


