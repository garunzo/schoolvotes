from django.test import TestCase

# Create your tests here.

from .models import Community, CommunityUser, Survey, Question, Response

# Create your tests here.
class ModelsTestCase(TestCase):

    def setUp(self):

      # Create communities.
      c1 = Community.objects.create(name="Samohi")
      c2 = Community.objects.create(name="Beverly Hills")

      # Create surveys.
      s1 = Survey.objects.create(community = c1, description="2018-Fall-ASB")
      s2 = Survey.objects.create(community = c2, description="2018-Winter-Athletics")

      # Create questions
      q11 = s1.add_question(rank = 1, text="What time should classes start?")
      q12 = s1.add_question(rank = 2, text="Should lunch be catered?")
      q21 = s2.add_question(rank = 1, text="Should badminton be added as a sport?")
      q22 = s2.add_question(rank = 2, text="What time should classes end?")

      # Add responses to questions
      r110 = q11.add_response(0, "7:00AM")
      r111 = q11.add_response(1, "8:00AM")
      r112 = q11.add_response(2, "9:00AM")

      r210 = q22.add_response(0, "2PM")
      r211 = q22.add_response(1, "3:00PM")

      r210.vote("luca")
      r210.vote("enzo")
      r211.vote("toby")

    def test_surveys_count(self):
        a = Survey.objects.all()
        self.assertEqual(a.count(), 2)

    def test_questions_count(self):
        a = Question.objects.all()
        self.assertEqual(a.count(), 4)

    def test_survey_get_questions_and_responses(self):
        s1 = Survey.objects.get(description="2018-Fall-ASB")
        s2 = Survey.objects.get(description="2018-Winter-Athletics")

        # retrieve the questions, should be ordered by rank
        questions_s1 = s1.get_questions()
        q_text = questions_s1[0].text()
        self.assertEqual(q_text, "What time should classes start?")
        self.assertTrue(len(questions_s1) == 2)
        responses_11 = questions_s1[0].get_responses()
        self.assertEqual(responses_11[1].text(), "8:00AM")

        questions_s2 = s2.get_questions()
        q_text = questions_s2[1].text()
        self.assertEqual(q_text, "What time should classes end?")
        self.assertTrue(len(questions_s2) == 2)
        responses_22 = questions_s2[1].get_responses()
        self.assertEqual(responses_22[1].text(), "3:00PM")
        
        self.assertEqual(responses_22[0].votes(), 2)
        self.assertEqual(responses_22[1].votes(), 1)
