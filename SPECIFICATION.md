## Background

I am a high school student who wants to improve student participation in decision making at my high school. My high school used paper ballots for us to use in order to make decisions. As a result of this, we did not conduct many surveys. The first production version was released 10/05/2018.

## Project location

* Source code: https://github.com/garunzo/schoolvotes
* Web site: http://schoolvotes.org/

## Project Description

My idea is to create a web-based voting application that will allow schools 
to rapidly conduct a survey of various topics. 

The application is able to use various authentication mechanisms, but 
currently uses google's authentication since my high school uses google 
for its email system.


## Target Customers

The target customers are schools that are using paper ballots to conduct 
surveys or vote for homecoming king and queen. 

The are two types of users:

1. Administrators - people who create the surveys.
2. Voters - people who vote on the surveys.

## Product Goals

* Provide inexpensive survey capability to public schools.
* Enable immediate feedback on survey results.
* Become a platform of communication within a school.
    * Provide weekly bulletin information.
* All students should log in weekly 

## Technical Requirements

1. Must allow students with or without phones to vote.
1. Administrators must be able to create various surveys.
    1. Create, read, update and delete surveys.
1. Administrators must be able to create question and responses.
    1. Create, read, update and delete questions and responses.
1. Administrators should be able to hide a survey.
    1. Allows administrators to create the survey before it becomes visible.
1. Surveys must be able to have unlimited questions.
1. Questions must allow multiple responses to the same question.
1. Allow over one thousand students to sign in within 15 seconds.
1. Survey result visibility can be controlled by the administrator.
    1. There are occasions in which the administrator will want to announce the results on a special occasion (e.g. homecoming king and queen).
1. Survey results should be available nearly realtime.
    1. For scalability, some caching may be used (memoization)
    1. The amount of delay should be adjustable by programmer.
1. Survey can be "opened" or "closed" at pre-specified times.
    1. There are occasions where the administrator may not want voting to start until a particular date and time.
    1. There are other occasions where the administrator may want to close voting after a specific date and time. 
1. Authentication should be referred to another agency.
    1. To ensure authenticity, the voters should be authenticated against an organizations mail system.
        1. Initially support google email accounts.
        1. Add other authentication as needed.
1. Keep a minimal amount of information regarding the voters.
    1. To maintain privacy, do not store information that is unnecessary for the operation of the system.
    1. Little information is required other than validating the validity / uniqueness of a voter.
1. Web pages should be dynamic and resize automatically depending on the end-user device being used.
1. Users can submit suggestions via email on the site.
1. Anonymous users can use a "contact us" email with captcha.
1. Database must be separate from the application.
    1. Allows multiple web/application servers to run in parallel.
    1. Combined with caching, numerous web/app servers can run in parallel with very little load on the database server.

### Tools
* Django/Channels is used as platform
   * Django uses the sqlite database
* Python is the primary server code
* HTML and Javascript are used for the front end
* Bootstrap templates were used for the navigation, etc.
* Google developer console (for authentication)
* Firebase

### Requirements
* Django==2.0.8
* Pillow
* django-allauth
* django-sslserver
* psycopg2
* psycopg2-binary


### Database
* Amazon RDS (Postgres) is used as the database
* The database has several tables
   * Community - this is the largest grouping
   * Survey - Surveys belong to communities and they can be hidden.
   * SurveyVoter - People who have voted on a survey (to count votes)
   * Question - Questions belong to surveys.
   * Response - Responses belong to questions. These are possible response selections for the given question.
   * ResponseVote - When a user votes for particular response, that vote is recorded here.


## TODOs / Limitations / Futures
* Add a feature that enables staff people to see hidden surveys.
