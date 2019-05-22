# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from django.contrib import admin
from django.forms import TextInput, Textarea
from .models import Community, Survey, Question, Response, ResponseVote, CommunityUser, SurveyVoter
from django.db import models
# Register your models here.

class CommunityAdmin(admin.ModelAdmin):
    attributes = {'rows': '4', 'cols': '40'}
    formfield_overrides = { models.CharField: {'widget': Textarea()},}

#    formfield_overrides = {
#        models.CharField: {'widget': Textarea(attrs={'rows':4, 'cols':80})}
#    }


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityUser)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(ResponseVote)
admin.site.register(SurveyVoter)
