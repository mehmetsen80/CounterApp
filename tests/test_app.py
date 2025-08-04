import unittest
from app import create_app
from enums.status_enum import StatusEnum

class CounterAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app.testing = True

    def test_home_endpoint(self):
        """Test the home endpoint"""
        response = self.client.get('/')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'CounterApp API')
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['version'], '1.0.0')
        self.assertEqual(data['environment'], 'testing')

    def test_health_endpoint(self):
        """Test the health endpoint"""
        response = self.client.get('/health')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['debug'])  # Should be True in testing config

    def test_get_count(self):
        """Test getting the count"""
        response = self.client.get('/api/v1/count')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', data)
        self.assertEqual(data['status'], StatusEnum.SUCCESS.value)
        self.assertIn('metadata', data)
        self.assertIn('value', data['metadata'])
        self.assertIn('last_updated', data['metadata'])

    def test_increment_count(self):
        """Test incrementing the count"""
        # Get initial count
        initial_response = self.client.get('/api/v1/count')
        initial_count = initial_response.get_json()['count']
        
        # Increment count
        response = self.client.get('/api/v1/count/increment')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], initial_count + 1)
        self.assertEqual(data['status'], StatusEnum.INCREMENTED.value)
        self.assertIn('metadata', data)

    def test_reset_count(self):
        """Test resetting the count"""
        # First increment to have a non-zero count
        self.client.get('/api/v1/count/increment')
        
        # Reset count
        response = self.client.get('/api/v1/count/reset')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['status'], StatusEnum.RESET.value)
        self.assertIn('metadata', data)

    def test_get_counter_details(self):
        """Test getting detailed counter information"""
        response = self.client.get('/api/v1/count/details')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], StatusEnum.SUCCESS.value)
        self.assertIn('counter', data)
        self.assertIn('value', data['counter'])
        self.assertIn('last_updated', data['counter'])
        self.assertIn('description', data['counter'])

if __name__ == '__main__':
    unittest.main() 