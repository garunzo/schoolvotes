# Project Overview

This project is a web site that allows communities to voted on various topics that are relevant to the members. It has two sections, the admin site. Admins are able to add surveys, etc.  Localhost/admin

The main page is for community members. They select a community and are presented with a list of active surveys on which they can vote. Note that currently, primarily for the testing simplicity, users can vote more than once.

The results page is kept current automatically using websockets. In order to reduce the amount of setup (i.e. no redis), the design currently just polls every 5 seconds from the client.

## Project design

### Tools
* Django/Channels is used as platform
   * Django uses the sqlite database
* Python is the primary server code
* HTML and Javascript are used for the front end
* Bootstrap templates were used for the navigation, etc.
* Google developer console (for authentication)
* Firebase

### Requirements
* Django==2.0.7
* Pillow
* channels - *Note that channels would not install in the IDE*
* django-allauth

* *For google authentication to work, I must have the testing hostname in my google API credentials.*  Currently I have,
   * http://localhost:8000
   * If others are needed for checking, please contact me so I can add it: luca.a.cotter@gmail.com

### Logins
* superuser
   * login: lucacotter
   * pwd:

### Main pages
* http://127.0.0.1:8000/
* http://127.0.0.1:8000/admin

### Database
* sqlite is used as the database
* The database has several tables
   * Community - this is the largest grouping
   * Survey - Surveys belong to communities and they can be hidden.
   * Question - Questions belong to surveys.
   * Response - Responses belong to questions. These are possible response selections for the given question.
   * ResponseVote - When a user votes for particular response, that vote is recorded here.

## Features
* Users select a community, then select a survey to vote on
* Users can sign on using Google.
   * https://console.developers.google.com/apis/credentials/
   * Currently the google client id is restricted to http://localhost:8000
   * JSON of the client id is below
   * Once the app is deployed, the localhost would be updated to the new app server name.
       * This is changed on google's console as well as in the admin area of django.
* Users submit votes or can view current voting results
   * Currently there is no lockout after someone has voted. This enables the same user to vote multiple times which greatly simplifies testing.
* Users can submit suggestions via email.
* Admin link on navigation bar appears only for people who are part of community staff.
* Admins can add communities, surveys, questions, responses.
* Admins can hide a survey so that it is not visible to users.
   * This can be used while preparing an survey for release
* Surveys can be hidden from view.
   * This allows a survey to be created in its entirety and only presented when ready.
* Web page resizes for mobile
* Voting results
   * Results update automatically without a page reload.
   * Channels / web sockets are used for communication

## Authentication Google
* Must update API origins https://console.developers.google.com/apis/credentials/ by adding new web server location (e.g. https://myapp.com or https://ide50-luc411.cs50.io:8080)
* Add a site to app server https://127.0.0.1/
* Update Social App in admin to include new site
* Update settings.py with site_id (this is from the site table in the admin section of django)

## TODOs / Limitations / Futures
* Add a feature that enables staff people to see hidden surveys.
* Add the ability to "close" a survey. This is when no more voting can occur.
* Allow multiple checkbox questions when voting.
* Change the polling over to leveragig redis and broadcasting vote changes to active clients.


## Files
```
.
├── README.md - This file
├── db.sqlite3 - Database
├── manage.py - Django management
├── media
│   └── logos - location where community logos are kept
│       └── samohi.jpeg
├── proposal.md - project proposal
├── requirements.txt - python requirements / dependencies
├── surveys - Main project information
│   ├── routing.py - for chat / websockets
│   ├── settings.py - project settings
│   ├── urls.py - routes
│   └── wsgi.py - web server gateway interface settings
└── votes - main app for project
    ├── __init__.py
    ├── admin.py - enables tables that can be admininstered by superusers
    ├── apps.py - application config def
    ├── consumers.py - socket consumers
    ├── forms.py - forms for login but not used for google interface
    ├── migrations - database updates
    ├── routing.py - chat / websockets
    ├── static
    │   └── votes - static files for votes
    │       ├── bars.css  - standard css including progress bars
    │       ├── bootstrap.css - bootstrap templates
    │       ├── bootstrap.js - bootstrap templates
    │       ├── jquery-3.js - bootstrap templates
    │       ├── popper.js - bootstrap templates
    │       ├── starter-template.css - bootstrap templates
    │       └── styles.css - original styles (obsolete)
    ├── templates
    │   ├── account
    │   │   └── login.html - login template
    │   ├── base.html - base html
    │   └── votes
    │       ├── allauthbase.html - allauth base html
    │       ├── chat.html - experimental
    │       ├── community.html - community main page
    │       ├── index.html - main page
    │       ├── logout.html - logout page (obsolete)
    │       ├── profile.html  - obsolete
    │       ├── results.html - results page (for surveys)
    │       ├── room.html - obsolete
    │       ├── signup.html - sign up page
    │       ├── suggestion.html - for submitting a suggestion
    │       ├── survey.html - survey page (where votes are cast)
    │       └── test.html - testing
    ├── tests.py - testing
    ├── urls.py - URL routes to view function mappings
    └── views.py - view code (between model and web pages)
 ```
Google API
```
```
