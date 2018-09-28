# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from .models import Community, Survey, Question, Response, ResponseVote, SurveyVoter
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from operator import itemgetter
import json
import os
from votes.memoize import MWT


from .forms import SignUpForm

TEST=False
# https://realpython.com/getting-started-with-django-channels/

# Create your views here. New view
def index(request):
    if request.user.is_authenticated:
        context = index_context(request)
        return render(request, 'votes/index.html', context)
    else:
        #return HttpResponse("You need to login")
        return redirect('account_login')

def index_context(request):
    context = {
        "username" : request.user.username,
        "firstname" : request.user.first_name.title(),
        "communities" : Community.get_communities_matching_email(request.user.email),
        "message" : "",
        "is_staff" : is_staff(request.user),
    }
    return context

def about(request):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        # community = Community.get_community(username)
        context = {
            "username" : username,
            "firstname" : request.user.first_name.title(),
            # "community" : community,
            "communities" : Community.get_communities_matching_email(email),
            "message" : "",
            "is_staff" : is_staff(request.user),
        }
        # if community is None:
        #     return render(request, 'votes/community.html', context)
        return render(request, 'votes/about.html', context)
    else:
        context = {
            "username" : "",
            "communities" : "", # User not authenticated
            "message" : "",
            "is_staff" : False,
        }
        return render(request, 'votes/about.html', context)

def select_community(request, community_id):
    if request.user.is_authenticated:
        username = request.user.username
        email = request.user.email
        community = Community.get_community_by_id(community_id)
        surveys = community.get_surveys_not_hidden()
        surveys_list_of_dict = []
        for survey in surveys:
            survey_dict = {}
            survey_dict['id'] = survey.id
            survey_dict['description'] = survey.get_description()
            survey_dict['max_votes'] = survey.get_max_votes()
            survey_dict['user_votes'] = survey.get_user_votes(email)
            survey_dict['results_hidden'] = survey.results_are_hidden
            survey_dict['is_closed'] = survey.is_closed()
            surveys_list_of_dict.append(survey_dict)
            print("is closed?", survey.is_closed())

        context = {
            "username" : username,
            "email": email,
            "firstname" : request.user.first_name.title(),
            "community" : community,
            "communities" : Community.get_communities_matching_email(email),
            "surveys" : surveys,
            "surveys_list_of_dict": surveys_list_of_dict,
            "is_staff" : is_staff(request.user),
        }
        return render(request, 'votes/community.html', context)
    return redirect('account_login')

def select_survey(request, survey_id):
    if request.user.is_authenticated or TEST:
        if TEST:
            username = "Luca"
            firstname = "Luca"
            email = "lac@smmk12.org"
            communities = Community.get_communities()
        else:
            username = request.user.username
            firstname = request.user.first_name.title()
            email = request.user.email
        survey = Survey.get_survey_by_id(survey_id)
        survey_open = not survey.is_closed()
        if (survey.user_authorized(email) and survey_open) or TEST:
            community = survey.get_community()
            questions = survey.get_questions()
            context = {
                "username" : username,
                "firstname" : firstname,
                "communities" : Community.get_communities_matching_email(email),
                "is_staff" : is_staff(request.user),
                "community" : community,
                "survey": survey,
                "questions" : questions,
            }
            return render(request, 'votes/survey.html', context)
        else:
            context = index_context(request)
            if survey_open:
                context['message'] = "You are not authorized to access that survey."
            else:
                context['message'] = "Sorry. No more voting permitted. Survey closed."
            return render(request, 'votes/index.html', context)
    return redirect('account_login')

def vote(request):
    if request.user.is_authenticated and request.method == "POST":
        username = request.user.username
        email = request.user.email
        keys = list(request.POST.keys())
        keys.remove('csrfmiddlewaretoken')

        # Make sure that the voter can still vote
        # (i.e. has not exceeded number of allowed votes)
        response = False
        status = False
        if len(keys) > 0:
            rid = request.POST[keys[0]][1:]
            response = Response.get_response_by_id(rid)
            if response.user_authorized(email):
                survey = response.get_survey()
                if survey.is_closed():
                    context = index_context(request)
                    context['message'] = "Sorry. No more voting permitted. Survey closed."
                    return render(request, 'votes/index.html', context)
                status, vote_count = SurveyVoter.update_vote_record(survey= survey,
                                               email=email, username=username)
                if not status:
                    message = "Sorry, you are not allowed to submit another vote."
            else:
                message = "You are not authorized to vote on this survey."
        else:
            message = "Sorry, your vote did not get recorded. " +\
                      "This is probably because no response was selected. " +\
                      "Please try to vote again."

        if status:
            # verify that the number of votes is correct for all questions
            submission_error = False
            for question in keys:
                qid = question[1:]
                question_record = Question.get_question_by_id(qid)
                response_limit = question_record.get_response_limit()
                responses = request.POST.getlist(question)
                if len(responses) > response_limit:
                    if not submission_error:
                        message = "Submission error: " + \
                                    question_record.text() + \
                                   ": too many selections"
                        submission_error = True
                    else:
                        message += ", " + question_record.text() + \
                                   ": too many selections"

            if not submission_error:
                for question in keys:
                    dictionary = request.POST.dict()
                    for response_code in request.POST.getlist(question):
                        rid = response_code[1:]
                        response = Response.get_response_by_id(rid)
                        response.vote(username, email)
                if response:
                    message = "Thank you for voting!"
            else:
                SurveyVoter.decr_vote_record(survey=survey, username=username,\
                                             email=email)

        context = {
            "username" : username,
            "firstname" : request.user.first_name.title(),
            "community" : None,
            "communities" : Community.get_communities_matching_email(email),
            "message" : message,
            "is_staff" : is_staff(request.user),
        }
        return render(request, 'votes/index.html', context)
    return redirect('account_login')

def test(request):
    if request.user.is_authenticated:
        username = request.user.username
        community = Community.get_community(username)
        context = {
            "username" : username,
            "firstname" : request.user.first_name.title(),
            "community" : community,
            "communities" : Community.get_communities_matching_email(email),
            "message" : "",
            "is_staff" : is_staff(request.user),
        }
    return render(request, 'votes/test.html', context)

def results(request, survey_id):
    if request.user.is_authenticated or TEST:
        if TEST:
            username = "Luca"
            firstname = "Luca"
            email = "lac@smmk12.org"
        else:
            username = request.user.username
            firstname = request.user.first_name.title()
            email = request.user.email

        survey = Survey.get_survey_by_id(survey_id)

        if survey and (not survey.results_are_hidden() or is_staff(request.user)):
            response_percents = Survey.get_response_percents(survey_id)
            context = {
                "username" : username,
                "firstname" : firstname,
                "survey" : survey,
                "communities" : Community.get_communities_matching_email(email),
                "is_staff" : is_staff(request.user),
                "response_percents" : response_percents,
            }
            return render(request, 'votes/results.v2.html', context)
        else:
            context = index_context(request)
            context['message'] = "You are not authorized to view those results."
            return render(request, 'votes/index.html', context)
    return redirect('account_login')



# def signout(request):
#     if request.user.is_authenticated:
#         username = request.user.username
#         logout(request)
#         context = {
#             "username" : username,
#             "is_staff" : is_staff(request.user),
#         }
#         return render(request, 'votes/logout.html', context)
#     return redirect('account_login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('account_login')
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
        "firstname" : request.user.first_name.title(),
        "is_staff" : is_staff(request.user),
    }
    return render(request, 'votes/room.html', context)

@MWT(60)
def is_staff(user):
    return user.groups.filter(name='Community Staff').exists()

def suggestion(request):
    if request.user.is_authenticated:
        email = request.user.email
        context = {
            "username" : request.user.username,
            "firstname" : request.user.first_name.title(),
            "is_staff" : is_staff(request.user),
            "communities" : Community.get_communities_matching_email(email),
        }
        return render(request, 'votes/suggestion.html', context)
    return redirect('account_login')

def mail(request):
    if request.user.is_authenticated and request.method == 'POST':
        context = {
            "username" : request.user.username,
            "firstname" : request.user.first_name.title(),
            "is_staff" : is_staff(request.user),
            "community" : None,
            "communities" : Community.get_communities_matching_email(email),
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
    return redirect('account_login')
