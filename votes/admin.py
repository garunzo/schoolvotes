from django.contrib import admin
from .models import Community, Survey, Question, Response, ResponseVote, CommunityUser
# Register your models here.

admin.site.register(Community)
admin.site.register(CommunityUser)
admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(ResponseVote)
