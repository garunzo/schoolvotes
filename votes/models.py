from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import datetime


# Create your models here.
class Community(models.Model):
    cid = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    # https://coderwall.com/p/bz0sng/simple-django-image-upload-to-model-imagefield
    logo = models.ImageField(upload_to = 'logos', default = 'logos/no-img.jpg')

    class Meta:
        verbose_name_plural = "Communities"

    def __str__(self):
        return f"Community Code: {self.cid}, Name: {self.name}, logo: {self.logo}"

    def get_surveys(self):
        return Survey.objects.filter(community=self).order_by('create_date_time')

    def get_surveys_not_hidden(self):
        return Survey.objects.filter(community=self, hide=False).order_by('create_date_time')

    @staticmethod
    def get_community_by_id(community_id):
        try:
            community = Community.objects.get(pk=community_id)
        except ObjectDoesNotExist:
            return None
        return community

    def get_name(self):
        return self.name

    @staticmethod
    def get_community(username):
        try:
            community = CommunityUser.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
        return community

    @staticmethod
    def get_communities():
        return Community.objects.all()

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
    hide = models.BooleanField(default=False)


    def __str__(self):
      return f"Survey: {self.description}, Community: {self.community.name}"

    def add_question(self, rank, text):
        question = Question(survey = self, _rank = rank, _text = text)
        question.save()
        return question

    def del_question(self, question):
        question.delete()

    def get_questions(self):
        return Question.objects.filter(survey=self).order_by('_rank')

    def get_description(self):
        return self.description

    def get_community(self):
        return self.community

    def isHidden(self):
        return self.hide

    @staticmethod
    def get_survey_by_id(survey_id):
        try:
            survey = Survey.objects.get(pk=survey_id)
        except ObjectDoesNotExist:
            return None
        return survey

    @staticmethod
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
                if num_votes != 0:
                    percent = int(response.votes() * 100.0 / num_votes)
                else:
                    percent = 0
                response_counts.append([rid, percent])
        return response_counts

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    _rank = models.IntegerField(default=0)
    _text = models.CharField(max_length=80)

    def __str__(self):
        # return f"Survey: {self.survey.description}, Rank: {self.rank}, Question Text: {self.text}"

        return f"Survey: , Rank: {self.rank()}, Question Text: {self.text()}"

    def get_responses(self):
        responses = Response.objects.filter(question=self).order_by('_rank')
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

class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    _rank = models.IntegerField(default = 0)
    _text = models.CharField(max_length=80)

    def __str__(self):
        return f"Survey: {self.question.survey.description}, Rank: {self.rank()}, Question: {self.question.text()}, Response: {self.text()}"

    def votes(self):
        return ResponseVote.objects.filter(response=self).count()

    def vote(self, username):
        vote = ResponseVote(response = self, question = self.question, username = username)
        vote.save()
        return True

    def rank(self):
        return self._rank

    def text(self):
        return self._text

    @staticmethod
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

    def __str__(self):
        return f"Survey: {self.response.question.survey.description}, Question Text: {self.response.question.text()}, Response Voted: {self.response.text()}"
