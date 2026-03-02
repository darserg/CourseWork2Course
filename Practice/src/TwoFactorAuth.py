from infrastructure.user_store import UserStore
from src.services.generator import CodeGenerator
from src.services.email_sender import EmailSender
from datetime import datetime
from typing import Dict
import secrets


class TwoFactorAuth:
    def __init__(self, user_store: UserStore):
        self.generator = CodeGenerator()
        self.email_sender = EmailSender()
        self.user_store = user_store
        self.codes: Dict[str, Dict] = {}
        self.max_attempts = 3

    def login(self, email: str, password: str) -> bool:
        """Первый этап: проверка логина и пароля"""
        return self.user_store.verify_user(email, password)

    def request_code(self, user_email: str) -> bool:
        """Второй этап: отправка кода 2FA"""
        # Проверяем, что пользователь существует
        if not self.user_store.get_user(user_email):
            return False

        code, expiry = self.generator.generate_with_expiry()
        self.codes[user_email] = {
            'code': code,
            'expiry': expiry,
            'attempts': 0
        }
        print(f"📧 Отправка кода на {user_email}...")
        return self.email_sender.send_verification_code(user_email, code)

    def verify_code(self, user_email: str, user_code: str) -> bool:
        """Третий этап: проверка кода 2FA"""
        if user_email not in self.codes:
            return False

        data = self.codes[user_email]

        if datetime.now() > data['expiry']:
            del self.codes[user_email]
            print("Код истёк.")
            return False

        if data['attempts'] >= self.max_attempts:
            del self.codes[user_email]
            print("Превышено количество попыток.")
            return False

        if secrets.compare_digest(data['code'], user_code.upper()):
            del self.codes[user_email]
            self.user_store.set_verified(user_email, True)  # ✅ Помечаем как верифицированного
            return True

        data['attempts'] += 1
        print(f"Неверный код. Осталось попыток: {self.max_attempts - data['attempts']}")
        return False