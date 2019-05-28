# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from operator import itemgetter
from django.utils import timezone
from django.utils.timezone import localtime
import gc


import datetime

from votes.memoize import MWT

MWT_TIMEOUT = 60
MWT_TIMEOUT_SURVEY_OPEN = 10


# Create your models here.
class Community(models.Model):
    cid = models.CharField(max_length=64, help_text='max chars = 64')
    name = models.CharField(max_length=64, help_text='max chars = 64')
    # https://coderwall.com/p/bz0sng/simple-django-image-upload-to-model-imagefield
    logo = models.ImageField(upload_to = 'logos', default = 'logos/no-img.jpg')
    emails = models.CharField(max_length=2048, blank=True, default='', help_text='max chars = 2048')

    class Meta:
        verbose_name_plural = "Communities"

    def __str__(self):
        return f"Community Code: {self.cid}, Name: {self.name}, logo: {self.logo}"

    @MWT(MWT_TIMEOUT)
    def get_surveys(self):
        return Survey.objects.filter(community=self).order_by('create_date_time')

    @MWT(MWT_TIMEOUT)
    def get_surveys_not_hidden(self):
        return Survey.objects.filter(community=self, hide=False).order_by('create_date_time')

    def get_emails(self):
        return self.emails

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_community_by_id(community_id):
        try:
            community = Community.objects.get(pk=community_id)
        except ObjectDoesNotExist:
            return None
        return community

    def get_name(self):
        return self.name

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_community(username):
        try:
            community = CommunityUser.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
        return community

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_communities():
        return Community.objects.all()

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_communities_matching_email(useremail):
        communities = Community.get_communities()
        community_list = []
        for community in communities:
            if community.email_authorized(useremail):
                community_list.append(community)
        return community_list

    @MWT(MWT_TIMEOUT)
    def email_authorized(self, useremail):
        email_list = list(filter(None, self.get_emails().split(';')))
        if len(email_list) == 0:
            return True
        else:
            for email in email_list:
                if email in useremail:
                    return True
        return False

    @MWT(MWT_TIMEOUT)
    def get_logo():
        path_elements = self.logo.split('/')
        print(path_elements)
        items = len(path_elements)
        print(path_elements[items-1])
        return path_elements[items-1]

class CommunityUser(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)


class Survey(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    description = models.CharField(max_length=80)
    create_date_time = models.DateTimeField(auto_now=False, auto_now_add=True)
    expiration_date_time = models.DateField(default=datetime.date.today)
    hide = models.BooleanField(default=False,
        help_text="Hide survey from community list")
    max_votes = models.IntegerField(default=0)
    results_hidden = models.BooleanField(default=False)
    survey_auto_open_close = models.BooleanField(default=False, \
        help_text="Set to true to close survey automatically based on " + \
                  "survey_open_datetime and survey_close_datetime. " + \
                  "Note that value is cached for " + str(MWT_TIMEOUT) + \
                  " seconds")
    survey_open_datetime = models.DateTimeField(default=timezone.now, null=True)
    survey_close_datetime = models.DateTimeField(default=timezone.now, null=True)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def is_closed(self):
        return self.survey_auto_open_close and \
               (timezone.now() < self.survey_open_datetime or \
               timezone.now() > self.survey_close_datetime)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def has_not_closed_yet(self):
        return self.survey_auto_open_close and (timezone.now() < self.survey_close_datetime)

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def get_open_datetime_str(self):
        return localtime(self.survey_open_datetime).strftime('%m-%d-%Y %I:%M %p')

    @MWT(MWT_TIMEOUT_SURVEY_OPEN)
    def get_close_datetime_str(self):
        return localtime(self.survey_close_datetime).strftime('%m-%d-%Y %I:%M %p')

    def __str__(self):
      return f"Survey: {self.description}, Community: {self.community.name}"

    def add_question(self, rank, text):
        question = Question(survey = self, _rank = rank, _text = text)
        question.save()
        return question

    def del_question(self, question):
        question.delete()

    @MWT(MWT_TIMEOUT)
    def get_questions(self):
        return Question.objects.filter(survey=self).order_by('_rank')

    @MWT(MWT_TIMEOUT)
    def get_description(self):
        return self.description

    def get_community(self):
        return self.community

    @MWT(MWT_TIMEOUT)
    def isHidden(self):
        return self.hide

    @MWT(MWT_TIMEOUT)
    def get_max_votes(self):
        return self.max_votes

    @MWT(MWT_TIMEOUT)
    def results_are_hidden(self):
        return self.results_hidden


    def get_user_votes(self, email):
        survey_voters = SurveyVoter.objects.filter(survey=self, email = email)
        if len(survey_voters) > 1:
            print("Inconsistency, more than one surveyvoter record.")
            return survey_voters[0].get_vote_count()
        elif len(survey_voters) == 1:
            return survey_voters[0].get_vote_count()
        else:
            return 0

    @MWT(MWT_TIMEOUT)
    def user_authorized(self, email):
        return self.community.email_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def user_athorized(email, sid):
        survey = Survey.get_survey_by_id(sid)
        return survey.user_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_survey_by_id(survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
        except ObjectDoesNotExist:
            return None
        return survey

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_response_percents(survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
        except ObjectDoesNotExist:
            return None
        response_counts = []
        for question in Question.objects.filter(survey = survey).order_by('_rank'):
            num_votes = 0
            for response in question.get_responses():
                num_votes += response.votes()
            for response in question.get_responses():
                rid = str(response.id)
                vote_count = response.votes()
                if num_votes != 0:
                    percent = int(vote_count * 100.0 / num_votes)
                else:
                    percent = 0
                response_counts.append([rid, percent, vote_count])
        return response_counts

class SurveyVoter(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=254,
                             blank=False)
    vote_count = models.IntegerField(default=1)
    created     = models.DateTimeField(editable=False)
    modified    = models.DateTimeField()

    def __str__(self):
        return f"Survey: {self.survey}, email: {self.email}, vote count: {self.vote_count}"

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(SurveyVoter, self).save(*args, **kwargs)

    def get_vote_count(self):
        return self.vote_count

    @classmethod
    def update_vote_record(cls, survey, username, email):
        with transaction.atomic():
            survey_voter, created = cls.objects.get_or_create(email = email, survey = survey,
                            defaults={'username':username})
            if not created:
                # survey_voter = (cls.objects.select_for_update().get(id=record.id))
                if survey.get_max_votes() == 0:
                    survey_voter.vote_count += 1
                    survey_voter.save()
                    status = True
                elif survey.get_max_votes() > survey_voter.vote_count:
                    survey_voter.vote_count += 1
                    survey_voter.save()
                    status = True
                else:
                    status = False
            else:
                # No voting had occurred, so okay to vote
                status = True
        return (status, survey_voter.vote_count)

    @classmethod
    def decr_vote_record(cls, survey, username, email):
        with transaction.atomic():
            survey_voter = cls.objects.get(email = email, survey = survey)
            survey_voter.vote_count -= 1
            survey_voter.save()
            status = True
        return status

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    _rank = models.IntegerField(default=0)
    _text = models.CharField(max_length=256)
    response_limit = models.IntegerField(default=1)

    def __str__(self):
        # return f"Survey: {self.survey.description}, Rank: {self.rank}, Question Text: {self.text}, id: {self.id}"

        return f"Survey: , Rank: {self.rank()}, Question Text: {self.text()}, qid: {self.id}"

    @MWT(MWT_TIMEOUT)
    def get_responses(self):
        responses = Response.objects.filter(question=self).order_by('_rank')
        return responses

    def get_responses_by_votes(self):
        responses = Response.objects.filter(question=self).order_by('_rank')
        response_list = []
        for response in responses:
            votes = response.votes()
            response_list.append([response, votes])
        response_list = sorted(response_list, key=itemgetter(1), reverse=True)
        responses = []
        for response in response_list:
            responses.append(response[0])
        return responses

    def rank(self):
        return self._rank

    def text(self):
        return self._text

    def has_voted(self, username):
        vote = ResponseVote.objects.filter(question = self, username = username)
        return len(vote) > 0

    def add_response(self, rank, text):
        response = Response(question = self, _rank = rank, _text = text)
        response.save()
        return response

    def get_survey(self):
        return self.survey

    @MWT(MWT_TIMEOUT)
    def get_response_limit(self):
        return self.response_limit

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_question_by_id(question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except ObjectDoesNotExist:
            return None
        return question

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    _rank = models.IntegerField(default = 0)
    _text = models.CharField(max_length=80)
    image_path = models.CharField(max_length=160, null=False, blank=True, default="")

    def __str__(self):
        return f"Survey: {self.question.survey.description}, Rank: {self.rank()}, Question: {self.question.text()}, Response: {self.text()}"

    def votes(self):
        return ResponseVote.objects.filter(response=self).count()

    def vote(self, username, email):
        vote = ResponseVote(response = self, question = self.question, username = username, email = email)
        vote.save()
        return True

    def rank(self):
        return self._rank

    def text(self):
        return self._text

    def get_survey(self):
        return self.question.get_survey()

    def get_image_path(self):
        return self.image_path

    def has_image(self):
        is_empty  = self.image_path in (None, '') or not self.image_path.strip()
        return not is_empty

    @MWT(MWT_TIMEOUT)
    def user_authorized(self, email):
        return self.question.survey.community.email_authorized(email)

    @staticmethod
    @MWT(MWT_TIMEOUT)
    def get_response_by_id(response_id):
        try:
            response = Response.objects.get(pk=response_id)
        except ObjectDoesNotExist:
            return None
        return response

class ResponseVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=254, null=True, blank=False)

    @staticmethod
    def batch_qs(qs, batch_size=1000):
        """
        Returns a (start, end, total, queryset) tuple for each batch in the given
        queryset.
    
        Usage:
            # Make sure to order your querset
            article_qs = Article.objects.order_by('id')
            for start, end, total, qs in batch_qs(article_qs):
                print "Now processing %s - %s of %s" % (start + 1, end, total)
                for article in qs:
                    print article.body
        """
        total = qs.count()
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            yield (start, end, total, qs[start:end])
            gc.collect()

    @staticmethod
    def queryset_iterator(queryset, chunksize=1000):
        pk = 0
        last_pk = queryset.order_by('-pk')[0].pk
        queryset = queryset.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()

    @staticmethod
    def dump_votes1(f):
        response_vote_qs = ResponseVote.objects.order_by('id')
        for start, end, total, qs in ResponseVote.batch_qs(response_vote_qs):
            for rv in qs:
                f.write(str(rv.csv_record()))
        return

    @staticmethod
    def dump_votes2(f):
        for rv in ResponseVote.queryset_iterator(ResponseVote.objects.all()):
            f.write(str(rv.csv_record())+"\n")
            f.flush()
        return 

    @staticmethod
    def dump_votes(f):
        for rv in ResponseVote.objects.order_by('id').all()[10000:15000]:
            f.write(str(rv.csv_record()))
            f.flush()
        return

    def csv_record(self):
        csv = str(self.id) + ", '" + self.response.question.survey.description + "', '" + self.response.question.text() + "', '" + self.response.text() + "', '" + self.username + "', '" + str(self.email) + "'\n"
        return csv

    def __str__(self):
        return f"Survey: {self.response.question.survey.description}, QText: {self.response.question.text()}, Response Voted: {self.response.text()}, Voter Username: {self.username}, Email: {self.email}"
