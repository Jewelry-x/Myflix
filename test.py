import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        # Create a test client
        self.app = app.test_client()

    def test_home_page(self):
        # Make a request to the home page
        response = self.app.get('/')

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if a specific element is present in the response data
        self.assertIn(b'<h1 style="text-align: center" class="display-2">Myflix2</h1>', response.data)

if __name__ == '__main__':
    unittest.main()
