from datetime import datetime
from random import shuffle

from django.shortcuts import  render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
#from django.template import RequestContext, loader

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from .models import Service, Ranking, Part, get_service, formating_part

from apps.reminder.views import json_dumps


@login_required
def temp_index(request):
    user = request.user
    ranking_user = Ranking.objects.filter(user = user)
    done = False
    for r in ranking_user :
        if r.rank != 0 and r.rank is not None :
            done = True
            break
    if done :
        return HttpResponseRedirect('/survey/run/top5-patients/')
        #return render(request, 'ranking_end.html') #temporaire, redirigeer vers suite du questionnaire?
    return render(request, 'presentation.html')

@login_required
def index(request):
    user = request.user
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





def selection_service(request):
    user = request.user
    services = list(Service.objects.all())
    shuffle(services)
    ranking_user = Ranking.objects.filter(user = user).filter(pertinency = 1)
    nb_ranked = ranking_user.count()
    context = {
        'services' : services,
        'user' : user,
        'ranking' : ranking_user,
        'ranking_size' : nb_ranked,
    }

    return render(request, 'questionnaire.html', context)

        # Verification de l'existence du rank pour service et user unique
        #si oui : MJ de la valeur de pertinency, RaZ du rang provisoire,modif_date = now,  verif rang = 0 ?
        #Si non : creation d'un nouvel objet avec user,service,  creation_date = now, pertinency = 1

@csrf_protect
def creation_rank(request):
    print(" rank creation")
    now = datetime.now()
    user = request.user
    service_id = request.POST.get('service', None)
    try:
        ranking_user = Ranking.objects.filter(user = user)
        print("ranking user has been found")
        if(ranking_user.filter(service_id = service_id).count() == 0):
            service = Service.objects.get(id = service_id)
            ranking_service = Ranking.objects.create(user = user, service_id = service, creation_date = now, pertinency = 0)
            data = {
                'action': "creation",
            }
            ranking_service.save()
        else:
            data = {
                'action': "nothing",
            }
        res = json_dumps(data)
    except Exception, e:
        res = "An error occurred during the creation :\n" + str(e)
    return HttpResponse(res, content_type="application/json")

@csrf_protect
def chgmt_statut_service(request):
    now = datetime.now()
    user = request.user
    service_id = request.POST.get('service', None)
    pertinency = request.POST.get('pertinency', None)
    print("service : "+ service_id)
    User_ranking = Ranking.objects.filter(user = user)
    try :
        data = {
            'exists': 1,
        }
        if(User_ranking.filter(service_id = service_id).count() != 0):
            ranking_service = User_ranking.get(service_id = service_id)
            ranking_service.pertinency = pertinency
            if pertinency == '0' :
                print("pertinency = 0")
                ranking_service.temporary_rank = 0
                ranking_service.rank = 0   # laisser pour les tests, mais ormalement pas besoin car rank n'est enregistre que a la fin?
            else:
                print("pertinency = 1 ?")

            if ranking_service.ranking_date :
                ranking_service.modif_date = now
                data.update({'action' : "modification"})
            else :
                ranking_service.ranking_date = now
                data.update({'action' : "selection"})

        else:
            service = Service.objects.get(id = service_id)
            ranking_service = Ranking.objects.create(user = user, service_id = service, creation_date = now, pertinency = 1)
            data.update({'action' : "creation"})
        ranking_service.save()
        nbRated = Ranking.objects.filter(user = user, pertinency = 1).count()
        data.update({'nbRated' : nbRated})
        test = json_dumps(data)
        status = 200
    except Exception, e:
        test = "An error occurred during the changement:\n" + str(e)
    return HttpResponse(test, content_type="application/json", status=status)

#Doit retourner la liste des questions + tester si il existe dans rank des donnees de ect utilisateur
@login_required
def ranking(request): #,action
    user = request.user
    ranking_user = Ranking.objects.filter(user = user)
    ranking = ranking_user.filter(pertinency = 1).order_by('temporary_rank')

    context = {
        'user' : user,
        'ranking' : ranking,
    }
    return render(request, 'ranking.html', context)

@csrf_protect
def saving_rank(request):
    now = datetime.now()
    if request.POST :
        post = request.POST
        user = request.user
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

    #return HttpResponse(service.text_html, mimetype="application/javascript")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@staff_member_required
def calcul_score(request, service_id):
    service = get_service(service_id)
    print(service)
    all_ranked = Ranking.objects.filter(service = service).filter(pertinency = 1)

    temp_text = ""
    for part in all_ranked :
        part_text = formating_part(part)
        temp_text = temp_text + part_text

    service.text_html = temp_text
    service.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


