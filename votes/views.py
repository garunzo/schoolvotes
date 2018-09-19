from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from .models import Community, Survey, Question, Response, ResponseVote
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
import json
import os


from .forms import SignUpForm

# https://realpython.com/getting-started-with-django-channels/

# Create your views here. New view
def index(request):
    if request.user.is_authenticated:
        username = request.user.username
        # community = Community.get_community(username)
        context = {
            "username" : username,
            # "community" : community,
            "communities" : Community.get_communities(),
            "message" : "",
            "is_staff" : is_staff(request.user),
        }
        # if community is None:
        #     return render(request, 'votes/community.html', context)
        return render(request, 'votes/index.html', context)
    else:
        #return HttpResponse("You need to login")
        return redirect('account_login')


def select_community(request, community_id):
    if request.user.is_authenticated:
        username = request.user.username
        community = Community.get_community_by_id(community_id)
        surveys = community.get_surveys_not_hidden()
        context = {
            "username" : username,
            "community" : community,
            "communities" : Community.get_communities(),
            "surveys" : surveys,
            "is_staff" : is_staff(request.user),
        }
        return render(request, 'votes/community.html', context)
    return redirect('login')

def select_survey(request, survey_id):
    if request.user.is_authenticated:
        username = request.user.username
        survey = Survey.get_survey_by_id(survey_id)
        community = survey.get_community()
        surveys = community.get_surveys_not_hidden()
        questions = survey.get_questions()
        context = {
            "username" : username,
            "community" : community,
            "communities" : Community.get_communities(),
            "survey": survey,
            "surveys" : surveys,
            "questions" : questions,
            "is_staff" : is_staff(request.user),
        }
        return render(request, 'votes/survey.html', context)
    return redirect('login')

def vote(request):
    if request.user.is_authenticated and request.method == "POST":
        username = request.user.username
        email = request.user.email
        keys = list(request.POST.keys())
        keys.remove('csrfmiddlewaretoken')
        for question in keys:
            rid = request.POST[question][1:]
            response = Response.get_response_by_id(rid)
            response.vote(username, email)

        context = {
            "username" : username,
            "community" : None,
            "communities" : Community.get_communities(),
            "message" : "Thank you for voting!",
            "is_staff" : is_staff(request.user),
        }
        return render(request, 'votes/index.html', context)
    return redirect('index')

def test(request):
    if request.user.is_authenticated:
        username = request.user.username
        community = Community.get_community(username)
        context = {
            "username" : username,
            "community" : community,
            "communities" : Community.get_communities(),
            "message" : "",
            "is_staff" : is_staff(request.user),
        }
    return render(request, 'votes/test.html', context)

def results(request, survey_id):
    if request.user.is_authenticated:
        username = request.user.username
        survey = Survey.get_survey_by_id(survey_id)
        community = survey.get_community()
        response_percents = Survey.get_response_percents(survey_id)
        context = {
            "username" : username,
            "survey" : survey,
            "community" : community,
            "communities" : Community.get_communities(),
            "is_staff" : is_staff(request.user),
            "response_percents" : response_percents,
        }
        return render(request, 'votes/results.v2.html', context)
    return redirect('login')

# def signout(request):
#     if request.user.is_authenticated:
#         username = request.user.username
#         logout(request)
#         context = {
#             "username" : username,
#             "is_staff" : is_staff(request.user),
#         }
#         return render(request, 'votes/logout.html', context)
#     return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'votes/signup.html', {'form': form})

def chat(request):
    return render(request, 'votes/chat.html', {})

def room(request, room_name):
    print(request.user.username)
    context = {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'username' : request.user.username,
        "is_staff" : is_staff(request.user),
    }
    return render(request, 'votes/room.html', context)

def is_staff(user):
    return user.groups.filter(name='Community Staff').exists()

def suggestion(request):
    if request.user.is_authenticated:
        context = {
            "username" : request.user.username,
            "is_staff" : is_staff(request.user),
            "communities" : Community.get_communities(),
        }
        return render(request, 'votes/suggestion.html', context)
    return redirect('account_login')

def mail(request):
    if request.user.is_authenticated and request.method == 'POST':
        context = {
            "username" : request.user.username,
            "is_staff" : is_staff(request.user),
            "community" : None,
            "communities" : Community.get_communities(),
            "message" : "Thanks for your suggestion!",
            "is_staff" : is_staff(request.user),
        }
        subject = "Community Suggestion"
        prologue = request.user.username + " from community web site suggests '"
        message = prologue + request.POST['message'] + "'"
        from_mail = 'fcbboardingpass@gmail.com'
        to = ['luca.a.cotter@gmail.com']
        password =  os.environ.get("MAIL_ACCOUNT_PWD", '')
        auth_user = 'boardingpassfcb@gmail.com'
        send_mail(subject, message, from_mail, to, fail_silently=False,
                  auth_user = auth_user, auth_password=password)
        return render(request, 'votes/index.html', context)
    return redirect('login')
