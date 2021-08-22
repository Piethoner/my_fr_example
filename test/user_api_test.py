import logging
logging.basicConfig(level=logging.INFO)

import unittest
import requests
from requests.auth import HTTPBasicAuth


class UserAPITest(unittest.TestCase):

    USER_API = 'http://127.0.0.1:5000/api/users'
    TOKEN_API = 'http://127.0.0.1:5000/api/token'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {
            'username': 'test',
            'password': 'test',
            'email': 'test@gmail.com'
        }

    @classmethod
    def setUpClass(cls):
        requests.delete(cls.USER_API)

    def test_create_user(self):
        logging.info('test create user')
        self.assertEqual(requests.post(self.USER_API, json=self.data).status_code, 200)
        self.assertEqual(requests.post(self.USER_API, json=self.data).status_code, 409)

    def test_query_users(self):
        logging.info('test query user')
        auth = HTTPBasicAuth(self.data['username'], self.data['password'])
        self.assertEqual(requests.get(self.USER_API, auth=auth).status_code, 200)
        self.assertEqual(requests.get(f'{self.USER_API}/1', auth=auth).status_code, 200)
        self.assertEqual(requests.get(f'{self.USER_API}/2', auth=auth).status_code, 410)
        token = requests.get(self.TOKEN_API, auth=auth).json().get('token')
        auth = HTTPBasicAuth(token, '')
        self.assertEqual(requests.get(self.USER_API, auth=auth).status_code, 200)


if __name__ == '__main__':
    unittest.main()


