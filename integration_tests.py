import unittest
from application import application
import json

class TestIntegration(unittest.TestCase):

    def test_ask_question(self):
        with application.app_context():
            data = {
                'query': "What are the latest advancements in breast cancer detection? ",
                'thread_id': '12345',

            }

            response = application.test_client().post('/askQuestion', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIsNotNone(response_data.get('answer'))
            self.assertIsNotNone(response_data.get('references'))
            self.assertIsNotNone(response_data.get('relevant_papers'))


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



