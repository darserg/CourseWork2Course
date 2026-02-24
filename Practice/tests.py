import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from generator import CodeGenerator
from email_sender import EmailSender
from main import TwoFactorAuth

class TestCodeGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CodeGenerator()

    def test_code_length(self):
        code = self.generator.generate()
        self.assertEqual(len(code), 6)

    def test_code_format(self):
        code = self.generator.generate()
        self.assertTrue(code.isalnum())
        self.assertEqual(code, code.upper())

    def test_expiry_time(self):
        expiry = self.generator.get_expiry_time()
        expected = datetime.now() + timedelta(minutes=5)
        self.assertAlmostEqual(expiry, expected, delta=timedelta(seconds=1))

class TestEmailSender(unittest.TestCase):
    @patch('email.smtplib.SMTP')
    def test_send_success(self, mock_smtp):
        sender = EmailSender()
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        result = sender.send_verification_code("test@example.com", "ABC123")
        self.assertTrue(result)

    @patch('email.smtplib.SMTP')
    def test_send_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception("SMTP Error")
        sender = EmailSender()
        result = sender.send_verification_code("test@example.com", "ABC123")
        self.assertFalse(result)

class TestTwoFactorAuth(unittest.TestCase):
    def setUp(self):
        self.auth = TwoFactorAuth()
        self.email = "test@example.com"

    @patch.object(EmailSender, 'send_verification_code', return_value=True)
    def test_request_code(self, mock_send):
        result = self.auth.request_code(self.email)
        self.assertTrue(result)
        self.assertIn(self.email, self.auth.codes)

    def test_verify_correct_code(self):
        self.auth.request_code(self.email)
        code = self.auth.codes[self.email]['code']
        self.assertTrue(self.auth.verify_code(self.email, code))
        self.assertNotIn(self.email, self.auth.codes)

    def test_verify_wrong_code(self):
        self.auth.request_code(self.email)
        self.assertFalse(self.auth.verify_code(self.email, "WRONG1"))
        self.assertEqual(self.auth.codes[self.email]['attempts'], 1)

    def test_verify_expired_code(self):
        self.auth.request_code(self.email)
        self.auth.codes[self.email]['expiry'] = datetime.now() - timedelta(minutes=10)
        self.assertFalse(self.auth.verify_code(self.email, "ABC123"))

    def test_max_attempts(self):
        self.auth.request_code(self.email)
        for _ in range(3):
            self.auth.verify_code(self.email, "WRONG1")
        self.assertNotIn(self.email, self.auth.codes)

if __name__ == '__main__':
    unittest.main()