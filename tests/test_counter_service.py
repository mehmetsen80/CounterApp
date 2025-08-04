import unittest
from services.counter_service import CounterService
from models.counter_model import Counter

class CounterServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.counter_service = CounterService()

    def test_initial_count(self):
        """Test initial count is 0"""
        count = self.counter_service.get_count()
        self.assertEqual(count, 0)

    def test_get_counter_object(self):
        """Test getting the full counter object"""
        counter = self.counter_service.get_counter()
        self.assertIsInstance(counter, Counter)
        self.assertEqual(counter.value, 0)
        self.assertIsNotNone(counter.last_updated)

    def test_get_counter_dict(self):
        """Test getting counter as dictionary"""
        counter_dict = self.counter_service.get_counter_dict()
        self.assertIn('value', counter_dict)
        self.assertIn('last_updated', counter_dict)
        self.assertIn('description', counter_dict)
        self.assertEqual(counter_dict['value'], 0)

    def test_increment_count(self):
        """Test incrementing count"""
        # Initial count should be 0
        self.assertEqual(self.counter_service.get_count(), 0)
        
        # Increment once
        count = self.counter_service.increment_count()
        self.assertEqual(count, 1)
        
        # Increment again
        count = self.counter_service.increment_count()
        self.assertEqual(count, 2)

    def test_reset_count(self):
        """Test resetting count"""
        # Increment a few times
        self.counter_service.increment_count()
        self.counter_service.increment_count()
        self.assertEqual(self.counter_service.get_count(), 2)
        
        # Reset
        count = self.counter_service.reset_count()
        self.assertEqual(count, 0)
        self.assertEqual(self.counter_service.get_count(), 0)

    def test_set_count(self):
        """Test setting count to specific value"""
        # Set to 5
        count = self.counter_service.set_count(5)
        self.assertEqual(count, 5)
        self.assertEqual(self.counter_service.get_count(), 5)
        
        # Set to 10
        count = self.counter_service.set_count(10)
        self.assertEqual(count, 10)
        self.assertEqual(self.counter_service.get_count(), 10)

if __name__ == '__main__':
    unittest.main() 