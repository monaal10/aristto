import unittest
from application import application
import json

class TestIntegration(unittest.TestCase):

    def test_ask_question(self):
        with application.app_context():
            data = {
                'query': 'What are deepfakes?',
            }
            response = application.test_client().post('/askQuestion', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIsNotNone(response_data.get('answer'))
            self.assertIsNotNone(response_data.get('references'))

    def test_literature_review(self):
        with application.app_context():
            data = {
                'query': 'Give me an overview of the research done around the topic deepfake detection',
                'start_year': 2010,
                'user_id': '1',
                'end_year': 2024,
                'citation_count': 5,
                'authors': None,
                'published_in': None
            }
            response = application.test_client().post('/getLiteratureReview', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIsNotNone(response_data.get('literatureReviewId'))
            self.assertIsNotNone(response_data.get('literatureReview'))
            self.assertIsNotNone(response_data.get('userId'))


    def test_login(self):
        with application.app_context():
            data = {
                'email': 'monaalsanghvi1998@gmail.com',
                'password': 'Abcd1234!',

            }
            response = application.test_client().post('/user/login', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)


    def test_chat(self):
        with application.app_context():
            data = {
                'query': 'Give me a summary',
                'paper_ids': ['W3047499317'],
                'conversation_history': []
            }
            response = application.test_client().post('/chatWithPapers', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)



