import unittest
import os
from user_store import UserStore

class TestUserStore(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_users.json"
        self.store = UserStore(self.test_db)
        self.test_email = "test@example.com"
        self.test_password = "securepass123"

    def tearDown(self):
        # Удаляем тестовый файл после каждого теста
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_register_new_user(self):
        result = self.store.register_user(self.test_email, self.test_password)
        self.assertTrue(result['success'])
        self.assertIsNotNone(self.store.get_user(self.test_email))

    def test_register_duplicate_user(self):
        self.store.register_user(self.test_email, self.test_password)
        result = self.store.register_user(self.test_email, "anotherpass")
        self.assertFalse(result['success'])

    def test_verify_correct_password(self): 
        self.store.register_user(self.test_email, self.test_password)
        self.assertTrue(self.store.verify_user(self.test_email, self.test_password))

    def test_verify_wrong_password(self):
        self.store.register_user(self.test_email, self.test_password)
        self.assertFalse(self.store.verify_user(self.test_email, "wrongpass"))

    def test_short_password_rejected(self):
        result = self.store.register_user(self.test_email, "123")
        self.assertFalse(result['success'])

    def test_set_verified(self):
        self.store.register_user(self.test_email, self.test_password)
        self.store.set_verified(self.test_email, True)
        user = self.store.get_user(self.test_email)
        self.assertTrue(user['is_verified'])

    def test_delete_user(self):
        self.store.register_user(self.test_email, self.test_password)
        self.assertTrue(self.store.delete_user(self.test_email))
        self.assertIsNone(self.store.get_user(self.test_email))


if __name__ == '__main__':
    unittest.main()