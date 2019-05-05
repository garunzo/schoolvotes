# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


from . import views
from django.contrib.auth import views as auth_views

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    path("", views.index, name="index"),
    path("index", views.index),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("privacy", views.privacy, name="privacy"),
    path("dump_votes", views.dump_votes, name="dump_votes"),
    path("battleroyale", views.battleroyale, name="battleroyale"),

    path("community/<int:community_id>", views.select_community, name="community"),
    path("survey/<int:survey_id>", views.select_survey, name="survey"),
    path("results/<int:survey_id>", views.results, name="results"),
    path("vote", views.vote, name="vote"),
    # path('signup/', views.SignUp.as_view(), name='signup'),
    # path('signup/', views.signup, name='signup'),
    # path('signout', views.signout, name='signout'),
    url(r'chat', views.chat, name='chat'),
    url(r'^room/(?P<room_name>[^/]+)/$', views.room, name='room'),
    path('test', views.test, name='test'),
    path('test/<int:id>', views.test, name='test-selection'),
    path('suggestion', views.suggestion, name='suggestion'),
    path('br_mail', views.suggestion, name='br_mail'),

    path('mail', views.mail, name='mail'),
    path('contact_mail', views.contact_mail, name='contact_mail'),

    url(r'^favicon\.ico$', favicon_view),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
